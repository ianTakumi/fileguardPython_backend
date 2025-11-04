from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subscription-plans', views.SubscriptionPlanViewSet, basename='subscription-plans')  # Changed from 'plans'
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')
router.register(r'user-profiles', views.UserProfileViewSet, basename='user-profiles')  # Changed from 'profile'

app_name = 'subscriptions'

urlpatterns = [
    path('', include(router.urls)),
     path('create-payment/', views.SubscriptionViewSet.as_view({'post': 'create_payment'}), name='create-payment'),
    path('execute-payment/', views.SubscriptionViewSet.as_view({'post': 'execute_payment'}), name='execute-payment'),
]