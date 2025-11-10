from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from utils.supabase_client import supabase
import json
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
def get_all_users(request):
    # Get users from Supabase Auth (using admin privileges)
    try:
        # Get all users from auth
        response = supabase.auth.admin.list_users()
        
        # Get all subscriptions from the subscriptions_subscription table
        subscriptions_response = supabase.table('subscriptions_subscription').select('*').execute()
        subscriptions = subscriptions_response.data if subscriptions_response.data else []
        
        # Create a mapping of user_id to subscription for easy lookup
        subscription_map = {}
        for subscription in subscriptions:
            if subscription and isinstance(subscription, dict):  # Check if subscription is valid dictionary
                user_id = subscription.get('user_id')
                if user_id:
                    subscription_map[user_id] = subscription
        
        # Map plan_id to plan name
        plan_mapping = {
            1: "free",
            2: "pro", 
            3: "business"
        }
        
        def serialize_user(user):
            """Helper function to serialize user object, including datetime objects"""
            # Get subscription data for this user
            user_subscription = subscription_map.get(user.id)
            
            # Default subscription data for free users
            default_subscription = {
                "id": None,
                "user_id": user.id,
                "status": "active",
                "start_date": None,
                "end_date": None,
                "created_at": None,
                "updated_at": None,
                "plan_id": 1,
                "plan_name": "free"
            }
            
            # If user has a subscription, use it; otherwise use default free plan
            if user_subscription:
                subscription_data = {
                    "id": user_subscription.get('id'),
                    "user_id": user_subscription.get('user_id'),
                    "status": user_subscription.get('status'),
                    "start_date": user_subscription.get('start_date'),
                    "end_date": user_subscription.get('end_date'),
                    "created_at": user_subscription.get('created_at'),
                    "updated_at": user_subscription.get('updated_at'),
                    "plan_id": user_subscription.get('plan_id', 1),  # Default to free if missing
                    "plan_name": plan_mapping.get(user_subscription.get('plan_id', 1), "free")
                }
            else:
                subscription_data = default_subscription
            
            user_dict = {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "aud": user.aud,
                "role": user.role,
                "is_anonymous": user.is_anonymous,
                "app_metadata": user.app_metadata,
                "user_metadata": user.user_metadata,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "confirmed_at": user.confirmed_at.isoformat() if user.confirmed_at else None,
                "email_confirmed_at": user.email_confirmed_at.isoformat() if user.email_confirmed_at else None,
                "phone_confirmed_at": user.phone_confirmed_at.isoformat() if user.phone_confirmed_at else None,
                "last_sign_in_at": user.last_sign_in_at.isoformat() if user.last_sign_in_at else None,
                "confirmation_sent_at": user.confirmation_sent_at.isoformat() if user.confirmation_sent_at else None,
                "recovery_sent_at": user.recovery_sent_at.isoformat() if user.recovery_sent_at else None,
                "email_change_sent_at": user.email_change_sent_at.isoformat() if user.email_change_sent_at else None,
                "new_email": user.new_email,
                "new_phone": user.new_phone,
                # Subscription data
                "subscription": subscription_data
            }
            return user_dict
        
        users = [serialize_user(user) for user in response]
        return JsonResponse(users, safe=False, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@csrf_exempt
@require_http_methods(["POST"])
def change_user_password(request):
    """
    API para magpalit ng password ng user sa Supabase Auth
    """
    try:
        # Kunin ang data mula sa request body
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_password = data.get('new_password')
        
        # Validation
        if not user_id:
            return JsonResponse({"error": "User ID ay kailangan"}, status=400)
        
        if not new_password:
            return JsonResponse({"error": "Bagong password ay kailangan"}, status=400)
        
        # I-validate ang strength ng password (optional pero recommended)
        if len(new_password) < 6:
            return JsonResponse({"error": "Password ay dapat hindi bababa sa 6 na characters"}, status=400)
        
        # Gamitin ang Supabase admin API para palitan ang password
        response = supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )
        
        # Check kung successful ang operation
        if hasattr(response, 'user') and response.user:
            return JsonResponse({
                "success": True,
                "message": "Password ay matagumpay na napalitan",
                "user_id": user_id
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "error": "Hindi matagumpay ang pagpapalit ng password"
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def upload_profile_picture(request, user_id):
    """
    API para mag-upload ng profile picture at i-save sa user metadata
    user_id ay nasa URL parameter
    """
    try:
        # Validation - check kung may user_id
        if not user_id:
            return JsonResponse({"error": "User ID ay kailangan"}, status=400)

        profile_picture = request.FILES.get('profile_picture')

        if not profile_picture:
            return JsonResponse({"error": "Profile picture ay kailangan"}, status=400)

        # I-validate ang file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_picture.content_type not in allowed_types:
            return JsonResponse({"error": "File type ay hindi suportado. Mga pinapayagan: JPEG, PNG, GIF, WebP"}, status=400)

        # I-validate ang file size (max 5MB)
        if profile_picture.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "File ay masyadong malaki. Maximum size: 5MB"}, status=400)

        # Generate unique filename
        file_extension = profile_picture.name.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"profile_{user_id}_{timestamp}.{file_extension}"

        # I-upload ang file sa Supabase storage bucket
        upload_response = supabase.storage.from_('uploads').upload(
            filename,
            profile_picture.read(),
            {"content-type": profile_picture.content_type}
        )

        # Check kung successful ang upload
        if hasattr(upload_response, 'error') and upload_response.error:
            return JsonResponse({"error": f"Upload failed: {upload_response.error}"}, status=400)
        
        # Kunin ang public URL
        try:
            public_url = supabase.storage.from_('uploads').get_public_url(filename)
            
            if isinstance(public_url, str):
                avatar_url = public_url
            else:
                avatar_url = public_url.public_url if hasattr(public_url, 'public_url') else f"https://{supabase.supabase_url}/storage/v1/object/public/uploads/{filename}"
                
        except Exception as upload_error:
            return JsonResponse({"error": f"Upload failed: {str(upload_error)}"}, status=400)

        # Kunin ang current user data
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        
        if not user_response.user:
            supabase.storage.from_('uploads').remove([filename])
            return JsonResponse({"error": "User hindi matagpuan"}, status=404)

        current_user = user_response.user
        current_metadata = current_user.user_metadata or {}

        # I-update ang user metadata para isama ang avatar URL
        updated_metadata = {**current_metadata, "avatar": avatar_url}

        # I-update ang user sa Supabase Auth
        update_response = supabase.auth.admin.update_user_by_id(
            user_id,
            {"user_metadata": updated_metadata}
        )

        if hasattr(update_response, 'user') and update_response.user:
            return JsonResponse({
                "success": True,
                "message": "Profile picture ay matagumpay na na-upload",
                "avatar_url": avatar_url,  # I-return lang ang avatar_url
            }, status=200)
        else:
            # Kung nabigo ang update, i-delete ang uploaded file
            supabase.storage.from_('uploads').remove([filename])
            return JsonResponse({
                "success": False,
                "error": "Hindi matagumpay ang pag-update ng user metadata"
            }, status=400)

    except Exception as e:
        # Kung may anumang error, i-delete ang uploaded file kung mayroon
        try:
            if 'filename' in locals():
                supabase.storage.from_('uploads').remove([filename])
        except:
            pass
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """
    API para mag-delete ng user sa Supabase Auth lang
    """
    try:
        # Validation - check kung may user_id
        if not user_id:
            return JsonResponse({"error": "User ID ay kailangan"}, status=400)

        # Diretso delete na sa Supabase Auth
        delete_response = supabase.auth.admin.delete_user(user_id)

        # Check kung successful
        if hasattr(delete_response, 'error') and delete_response.error:
            return JsonResponse({
                "success": False,
                "error": f"Hindi matagumpay ang pag-delete: {delete_response.error}"
            }, status=400)

        return JsonResponse({
            "success": True,
            "message": "User ay matagumpay na nai-delete sa Supabase Auth",
            "user_id": user_id
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["GET"])
def count_total_users(request):
    """
    API para makuha ang total number ng mga user sa Supabase Auth
    """
    try:
        # Kunin ang listahan ng mga user mula sa Supabase
        response = supabase.auth.admin.list_users()
        
        # Debug: Check the response structure
        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")
        
        # Iba't ibang paraan para makuha ang users list
        users = None
        
        # Try different ways to access the users data
        if hasattr(response, 'users'):
            users = response.users
            print(f"Found users via response.users: {len(users)}")
        elif hasattr(response, 'data'):
            users = response.data
            print(f"Found users via response.data: {len(users)}")
        elif isinstance(response, list):
            users = response
            print(f"Response is a list: {len(users)}")
        else:
            # Try to access directly
            try:
                users = response
                print(f"Using response directly: {len(users)}")
            except:
                pass
        
        # Bilangin ang total users
        if users is not None:
            total_users = len(users)
            
            return JsonResponse({
                "success": True,
                "total_users": total_users,
                "message": f"May kabuuang {total_users} na user"
            }, status=200)
        else:
            # Alternative: Gamitin ang get_all_users logic
            print("Trying alternative approach...")
            try:
                auth_response = supabase.auth.admin.list_users()
                # Assume same structure as get_all_users
                if hasattr(auth_response, 'users'):
                    total_users = len(auth_response.users)
                    return JsonResponse({
                        "success": True,
                        "total_users": total_users,
                        "message": f"May kabuuang {total_users} na user"
                    }, status=200)
            except Exception as alt_e:
                print(f"Alternative approach failed: {alt_e}")
            
            return JsonResponse({
                "success": False,
                "error": "Hindi makuha ang listahan ng mga user",
                "debug_info": f"Response type: {type(response)}"
            }, status=400)
            
    except Exception as e:
        print(f"Error in count_total_users: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)