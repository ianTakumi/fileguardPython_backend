from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from utils.supabase_client import supabase
from utils.utils import encrypt_file, decrypt_file
from .models import File, FileShare
from .serializers import FileSerializer, FileShareSerializer
import tempfile, os
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from collections import Counter

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            # Get files owned by user OR shared with user
            return File.objects.filter(
                Q(user_id=user_id) | 
                Q(shares__shared_with_id=user_id)
            ).distinct()
        return File.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.query_params.get('user_id') or self.request.data.get('user_id')
        return context

    def create(self, request, *args, **kwargs):
        uploaded_files = request.FILES.getlist('files')
        user_id = request.data.get('user_id')
        is_private = request.data.get('is_private', True)
        
        if not uploaded_files:
            return Response({'error': 'No files provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        created_files = []
        errors = []

        for uploaded_file in uploaded_files:
            temp_path = None
            try:
                # 1️⃣ Create temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                    for chunk in uploaded_file.chunks():
                        temp_file.write(chunk)
                    temp_path = temp_file.name

                # 2️⃣ Encrypt the file
                encrypt_file(temp_path)

                # 3️⃣ Upload to Supabase with conflict handling
                bucket_name = "uploads"
                file_name = uploaded_file.name

                def upload_with_retry(name, attempt=1):
                    try:
                        supabase.storage.from_(bucket_name).upload(
                            path=name,
                            file=temp_path,
                            file_options={"content-type": uploaded_file.content_type}
                        )
                        return name
                    except Exception as e:
                        if "409" in str(e) or "Resource already exists" in str(e):
                            base, ext = os.path.splitext(name)
                            new_name = f"{base} ({attempt}){ext}"
                            return upload_with_retry(new_name, attempt + 1)
                        raise e

                final_name = upload_with_retry(file_name)

                # 4️⃣ Get public URL
                file_url = supabase.storage.from_(bucket_name).get_public_url(final_name)

                # 5️⃣ Create DB record with is_private field
                file_instance = File.objects.create(
                    user_id=user_id,
                    name=final_name,
                    file=file_url,
                    size=uploaded_file.size,
                    is_private=is_private
                )

                created_files.append(file_instance)

            except Exception as e:
                errors.append({
                    'file_name': uploaded_file.name,
                    'error': str(e)
                })
            
            finally:
                # 6️⃣ Cleanup
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

        if created_files:
            serializer = FileSerializer(created_files, many=True)
            response_data = {
                'success': True,
                'created_files': serializer.data,
                'total_created': len(created_files)
            }
            if errors:
                response_data['errors'] = errors
                response_data['partial_success'] = True
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)

    # 🆕 Toggle Star/Unstar file
    @action(detail=True, methods=['post'], url_path='toggle-star', permission_classes=[permissions.AllowAny])
    def toggle_star(self, request, pk=None):
        file = get_object_or_404(File, pk=pk)
        file.isStarred = not file.isStarred
        file.save()
        
        return Response({
            'success': True,
            'file_id': file.id,
            'file_name': file.name,
            'isStarred': file.isStarred
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='share', permission_classes=[permissions.AllowAny])
    def share_file(self, request, pk=None):
        shared_with_email = request.data.get('shared_with_email')
        owner_id = request.data.get('owner_id')
        
        if not shared_with_email:
            return Response({'error': 'shared_with_email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not owner_id:
            return Response({'error': 'owner_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify that the file exists and user owns it
        try:
            file = File.objects.get(id=pk, user_id=owner_id)
        except File.DoesNotExist:
            return Response({'error': 'File not found or you do not own this file'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # 🆕 List users - it returns a list directly
            users_list = supabase.auth.admin.list_users()
            
            print(f"Found {len(users_list)} users")  # Debug
            print("Users:", users_list)  # Debug
            
            target_user = None
            for user in users_list:  # Directly iterate over the list
                print(f"Checking user: {user.email}")  # Debug
                if user.email == shared_with_email:
                    target_user = user
                    break
            
            if not target_user:
                return Response({'error': 'User with this email not found in Supabase Auth'}, status=status.HTTP_404_NOT_FOUND)
            
            shared_with_uuid = target_user.id
            print(f"Found user ID: {shared_with_uuid}")  # Debug
            
            # Check if already shared
            if FileShare.objects.filter(file=file, shared_with_id=shared_with_uuid).exists():
                return Response({'error': 'File already shared with this user'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create share record
            share = FileShare.objects.create(
                file=file,
                owner_id=owner_id,
                shared_with_id=shared_with_uuid
            )
            
            serializer = FileShareSerializer(share)
            return Response({
                'success': True,
                'message': f'File shared successfully with {shared_with_email}',
                'share': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error details: {str(e)}")  # Debug
            return Response({'error': f'Failed to find user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # 🆕 Get shared files for a user
    @action(detail=False, methods=['get'], url_path='shared-with-me', permission_classes=[permissions.AllowAny])
    def shared_with_me(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        shared_files = FileShare.objects.filter(shared_with_id=user_id).select_related('file')
        serializer = FileShareSerializer(shared_files, many=True)
        
        return Response({
            'success': True,
            'shared_files': serializer.data,
            'total_shared': len(serializer.data)
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='unshare', permission_classes=[permissions.AllowAny])
    def unshare_file(self, request, pk=None):
        shared_with_email = request.data.get('shared_with_email')
        owner_id = request.data.get('owner_id')
        
        if not shared_with_email:
            return Response({'error': 'shared_with_email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not owner_id:
            return Response({'error': 'owner_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify that the file exists and user owns it
        try:
            file = File.objects.get(id=pk, user_id=owner_id)
        except File.DoesNotExist:
            return Response({'error': 'File not found or you do not own this file'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # 🆕 Get user UUID from Supabase Auth by email
            users_list = supabase.auth.admin.list_users()
            
            target_user = None
            for user in users_list:  # Direct iteration over the list
                if user.email == shared_with_email:
                    target_user = user
                    break
            
            if not target_user:
                return Response({'error': 'User with this email not found in Supabase Auth'}, status=status.HTTP_404_NOT_FOUND)
            
            shared_with_uuid = target_user.id
            
            # Delete share record
            share = get_object_or_404(FileShare, file=file, shared_with_id=shared_with_uuid)
            share.delete()
            
            return Response({
                'success': True,
                'message': f'File unshared successfully with {shared_with_email}'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'Failed to find user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 🆕 Update file privacy
    @action(detail=True, methods=['post'], url_path='set-privacy', permission_classes=[permissions.AllowAny])
    def set_privacy(self, request, pk=None):
        file = get_object_or_404(File, pk=pk)
        is_private = request.data.get('is_private')
        user_id = request.data.get('user_id')
        
        if is_private is None:
            return Response({'error': 'is_private field is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user owns the file
        if str(file.user_id) != user_id:
            return Response({'error': 'You can only modify privacy of files you own'}, status=status.HTTP_403_FORBIDDEN)
        
        file.is_private = is_private
        file.save()
        
        return Response({
            'success': True,
            'file_id': file.id,
            'file_name': file.name,
            'is_private': file.is_private
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='count-all', permission_classes=[permissions.AllowAny])
    def count_all_files(self, request):
        count = File.objects.count()
        return Response({'total_files': count}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='total-size', permission_classes=[permissions.AllowAny])
    def total_size_by_user(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_size = File.objects.filter(user_id=user_id).aggregate(total=Sum('size'))['total'] or 0
            return Response({'user_id': user_id, 'total_size': total_size}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    @action(detail=True, methods=['get'], url_path='download', permission_classes=[permissions.AllowAny])
    def download_file(self, request, pk=None):
            file = get_object_or_404(File, pk=pk)
            
            try:
                # Download from Supabase
                bucket_name = "uploads"
                encrypted_content = supabase.storage.from_(bucket_name).download(file.name)
                
                if not encrypted_content:
                    return Response({'error': 'File not found in storage'}, status=status.HTTP_404_NOT_FOUND)
                
                # Create a temporary file to use with your decrypt_file function
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(encrypted_content)
                    temp_path = temp_file.name
                
                try:
                    # 🔐 DECRYPT THE FILE CONTENT using your existing function
                    decrypted_content = decrypt_file(temp_path)
                    
                    # Create response with decrypted file
                    response = HttpResponse(decrypted_content, content_type='application/octet-stream')
                    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
                    return response
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
  # 🆕 Get top 5 file types by extracting from filename
    @action(detail=False, methods=['get'], url_path='top-file-types', permission_classes=[permissions.AllowAny])
    def top_file_types(self, request):
        try:
            # Get all files
            files = File.objects.all()
            
            # Extract file extensions from names
            extensions = []
            for file in files:
                if file.name:
                    # Get file extension using os.path.splitext
                    _, ext = os.path.splitext(file.name)
                    if ext:
                        # Remove the dot and convert to lowercase
                        ext = ext.lower().lstrip('.')
                        extensions.append(ext if ext else 'no_extension')
                    else:
                        extensions.append('no_extension')
                else:
                    extensions.append('unknown')
            
            # Count occurrences and get top 5
            extension_counter = Counter(extensions)
            top_5 = dict(extension_counter.most_common(5))
            
            return Response(top_5, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch top file types: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )