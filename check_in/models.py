from django.db import models
from subscription.models import Subscription
from helpers.models import BaseModel
from django.utils import timezone

# Create your models here.
class CheckIn(BaseModel):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='check_ins', null=False, blank=False)
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=True, blank=True)
    expiry_date_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription_id.user_id.user_name} - {self.start_time} - {self.end_time} - {self.expiry_date_time}"

    def is_expired(self):
        return self.expiry_date_time < timezone.now()