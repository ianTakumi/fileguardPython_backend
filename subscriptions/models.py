# models.py
from django.db import models

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium')
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interval_days = models.IntegerField(default=30)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        CANCELED = 'canceled', 'Canceled'
        EXPIRED = 'expired', 'Expired'
    
    # Use CharField for Supabase user_id instead of ForeignKey
    user_id = models.CharField(max_length=255, db_index=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.ACTIVE
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_id', 'plan']

    def __str__(self):
        return f"{self.user_id} - {self.plan.name}"