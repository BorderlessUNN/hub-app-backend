from django.db import models
from django.utils import timezone
from helpers.models import BaseModel
from accounts.models import CustomUser
from django.utils.text import slugify


class Plans(BaseModel):
    name = models.CharField(max_length=20)
    price = models.IntegerField(null=False, blank=False)
    hours = models.IntegerField(null=False, blank=False)
    slug  = models.SlugField( blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

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
