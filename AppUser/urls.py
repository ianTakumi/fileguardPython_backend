# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get-users/', views.get_all_users, name='get_users'),
    path('change-password/', views.change_user_password, name="change_user_password"),
    path('upload-profile-picture/<str:user_id>/', views.upload_profile_picture, name='upload_profile_picture'),
    path('delete/<str:user_id>/', views.delete_user, name='delete_user'), 
    path('count-total-users/', views.count_total_users, name='count_total_users'),
]
