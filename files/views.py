from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.http import HttpResponse
from .models import File
from .serializers import FileSerializer
from utils.utils import encrypt_file, decrypt_file
from rest_framework.decorators import action
class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show only the files belonging to the logged-in user
        return File.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Save the file and encrypt it right away
        file_instance = serializer.save(user=self.request.user)
        encrypt_file(file_instance.file.path)

    def retrieve(self, request, *args, **kwargs):
        # Decrypt file when downloading
        instance = self.get_object()
        decrypted_content = decrypt_file(instance.file.path)

        response = HttpResponse(decrypted_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{instance.name}"'
        return response

    @action(
        detail=False,
        methods=['get'],
        url_path='count-all',
        permission_classes=[permissions.AllowAny] 
    )
    def count_all_files(self, request):
        """Return total number of files in the system (publicly accessible)"""
        token = request.headers.get('Authorization')
        print("🔐 Bearer Token:", token)  # 👈 This prints the full token to the console

        count = File.objects.count()
        return Response({'total_files': count}, status=status.HTTP_200_OK)
