from django.db import models
from django.utils import timezone
from helpers.models import BaseModel
from accounts.models import CustomUser


class Plans(BaseModel):
    name = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hours = models.IntegerField(null=False, blank=False)


class Payment(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    plan = models.ForeignKey(
        Plans,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    expires_at = models.DateTimeField(null=False, blank=False)

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()
