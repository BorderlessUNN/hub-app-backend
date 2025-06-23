from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

class CheckIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='checkins')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.user_name} checked in at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
