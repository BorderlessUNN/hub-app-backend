from django.db import models
from helpers.models import BaseModel
from django.utils import timezone
from subscription.models import Subscription
from django.db.models import F
from django.db import transaction

# Create your models here.
class HubClosureDate(BaseModel):
    date = models.DateField( unique=True)
    reason = models.TextField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date)

    def is_closed(self):
        return self.date < timezone.now().date()

    