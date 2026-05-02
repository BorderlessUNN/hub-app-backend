from django.db import models
from helpers.models import BaseModel
from accounts.models import CustomUser
from payments.models import Payment, Plans
from django.utils import timezone

# Create your models here.
class Subscription(BaseModel):
    class SubscriptionStatus(models.TextChoices):
        PARTIAL_ACTIVE = 'Partial Active', 'Partial Active'
        ACTIVE = 'Active', 'Active'
        EXPIRED = 'Expired', 'Expired'
        EXPIRED_PARTIAL = 'Expired Partial', 'Expired Partial'
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE, related_name='subscriptions')
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='subscriptions', null=True, blank=True)
    admin_assigned = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=SubscriptionStatus.choices, blank = False, null = False)
    expires_at = models.DateTimeField(null=True, blank=True)
    partial_expires_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        if self.status == self.SubscriptionStatus.EXPIRED:
            return True
        elif self.status == self.SubscriptionStatus.EXPIRED_PARTIAL:
            return self.partial_expires_at < timezone.now()
        else:
            return False