# serializers.py
from rest_framework import serializers
from .models import SubscriptionPlan, Subscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='plan',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user_id', 'plan', 'plan_id', 'status', 
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'start_date', 'end_date', 'created_at', 'updated_at']

class UserSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    subscription = SubscriptionSerializer()