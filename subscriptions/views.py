from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SubscriptionPlan, Subscription
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    UserSubscriptionSerializer
)
from .paypal_service import PayPalService
from django.conf import settings


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = []

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = []
    http_method_names = ['get', 'post', 'patch']
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Subscription.objects.filter(user_id=user_id)
        return Subscription.objects.none()
    
    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        if not user_id:
            raise serializers.ValidationError({'user_id': 'This field is required'})
        
        # Auto-assign free plan if none provided
        if not serializer.validated_data.get('plan'):
            free_plan = SubscriptionPlan.objects.filter(tier='free').first()
            if free_plan:
                serializer.save(user_id=user_id, plan=free_plan)
                return
        
        serializer.save(user_id=user_id)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's subscription - auto creates free if doesn't exist"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = Subscription.objects.get(user_id=user_id)
        except Subscription.DoesNotExist:
            # Auto-create free subscription
            free_plan = SubscriptionPlan.objects.filter(tier='free').first()
            if not free_plan:
                free_plan = SubscriptionPlan.objects.create(
                    name='Free Plan',
                    tier='free',
                    price=0.00,
                    interval_days=36500,
                    features=['Basic features']
                )
            subscription = Subscription.objects.create(user_id=user_id, plan=free_plan)
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Upgrade to a paid plan"""
        user_id = request.data.get('user_id')
        plan_id = request.data.get('plan_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not plan_id:
            return Response(
                {'error': 'plan_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            subscription = Subscription.objects.get(user_id=user_id)
            
            if new_plan.tier == 'free':
                return Response(
                    {'error': 'Cannot upgrade to free plan'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            subscription.plan = new_plan
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
            
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Plan not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def downgrade(self, request):
        """Downgrade to free plan"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        free_plan = SubscriptionPlan.objects.filter(tier='free').first()
        
        if not free_plan:
            free_plan = SubscriptionPlan.objects.create(
                name='Free Plan',
                tier='free',
                price=0.00,
                interval_days=36500,
                features=['Basic features']
            )
        
        try:
            subscription = Subscription.objects.get(user_id=user_id)
            subscription.plan = free_plan
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()
        except Subscription.DoesNotExist:
            subscription = Subscription.objects.create(user_id=user_id, plan=free_plan)
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
   # subscriptions/views.py
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Create PayPal payment for upgrade"""
        user_id = request.data.get('user_id')
        plan_id = request.data.get('plan_id')
        
        if not user_id or not plan_id:
            return Response(
                {'error': 'user_id and plan_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create PayPal payment
            return_url = f"{settings.FRONTEND_URL}/subscription/success"
            cancel_url = f"{settings.FRONTEND_URL}/subscription/cancel"
            
            payment = PayPalService.create_payment(
                plan_id=plan_id,
                user_id=user_id,
                return_url=return_url,
                cancel_url=cancel_url
            )
            
            return Response({
                'payment_id': payment['id'],
                'approval_url': payment['approval_url'],
                'status': payment['status']
            })
            
        except Exception as e:
            print(f"💥 View error: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def execute_payment(self, request):
        """Execute payment after user approval"""
        order_id = request.data.get('order_id')
        user_id = request.data.get('user_id')
        plan_id = request.data.get('plan_id')
        
        try:
            # Execute PayPal payment
            payment = PayPalService.execute_payment(order_id)
            
            if payment['status'] == 'COMPLETED':
                # Update user subscription
                new_plan = SubscriptionPlan.objects.get(id=plan_id)
                
                subscription = Subscription.objects.get(user_id=user_id)
                subscription.plan = new_plan
                subscription.status = Subscription.Status.ACTIVE
                subscription.save()
                
                return Response({
                    'message': 'Payment successful and subscription upgraded',
                    'subscription': SubscriptionSerializer(subscription).data
                })
            else:
                return Response(
                    {'error': 'Payment not completed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
class UserProfileViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class = UserSubscriptionSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get user with subscription info"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure user has subscription
        try:
            Subscription.objects.get(user_id=user_id)
        except Subscription.DoesNotExist:
            # Auto-create free subscription
            free_plan = SubscriptionPlan.objects.filter(tier='free').first()
            if not free_plan:
                free_plan = SubscriptionPlan.objects.create(
                    name='Free Plan',
                    tier='free',
                    price=0.00,
                    interval_days=36500,
                    features=['Basic features']
                )
            Subscription.objects.create(user_id=user_id, plan=free_plan)
        
        # Create mock user data for response
        user_data = {
            'id': user_id,
            'username': f'user_{user_id}',
            'email': f'user_{user_id}@example.com',
            'subscription': Subscription.objects.get(user_id=user_id)
        }
        
        serializer = self.get_serializer(user_data)
        return Response(serializer.data)
    
    
    