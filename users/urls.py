from django.urls import path
from .views import UserListCreateView, UserDetailView, UserRegistrationView, UserUpdateView, UserDeleteView

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/update/', UserUpdateView.as_view(), name='user-update'),
    path('profile/delete/', UserDeleteView.as_view(), name='user-delete'),
]
