from django.db import models
from helpers.models import BaseModel
from accounts.models import CustomUser

from django.utils import timezone

# Create your models here.
class Subscription(BaseModel):
    class SubscriptionStatus(models.TextChoices):
        PARTIAL_ACTIVE = 'Partial Active', 'Partial Active'
        ACTIVE = 'Active', 'Active'
        PENDING = 'Pending', 'Pending'
        EXPIRED = 'Expired', 'Expired'
        EXPIRED_PARTIAL = 'Expired Partial', 'Expired Partial'
        FAILED = 'Failed', 'Failed'

    # Statuses that count as "already has a subscription in flight" - used to
    # block a member from starting a second one while one of these is open.
    OPEN_STATUSES = (SubscriptionStatus.PENDING, SubscriptionStatus.PARTIAL_ACTIVE, SubscriptionStatus.ACTIVE)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey("payments.Plans", on_delete=models.CASCADE, related_name='subscriptions')
    admin_assigned = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=SubscriptionStatus.choices,default=SubscriptionStatus.PENDING, blank = False, null = False)
    expires_at = models.DateTimeField(null=True, blank=True)
    partial_expires_at = models.DateTimeField(null=True, blank=True)
    # Only set for non-member bookings: number of hours purchased at
    # ₦/hour (see Plans.price for the hourly rate), used at check-in time
    # to compute the session's expiry window instead of a fixed plan.hours.
    hours = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.expires_at and self.expires_at < timezone.now():
            self.status = self.SubscriptionStatus.EXPIRED
        elif self.partial_expires_at and self.partial_expires_at < timezone.now():
            self.status = self.SubscriptionStatus.EXPIRED_PARTIAL
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.user_name} - {self.plan.name} - {self.status}"

    
