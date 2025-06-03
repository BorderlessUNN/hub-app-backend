from django.db import models
from django.utils import timezone
from django.db import transaction

from helpers.models import BaseModel


class CustomUser(BaseModel):
    """
    Custom user model
    """
    # Exclude unnecessary fields from the abstract user model    

    user_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with this email already exists."
        }
    )
    department = models.CharField(max_length=200)
    whatsapp_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    last_checkin = models.DateField(blank=True, null=True)
    tech_stack = models.CharField(max_length=200)
  
    def delete(self, *args, **kwargs):
        """
        Soft deletes the user and modifies the email for reference.
        """
        with transaction.atomic():
            self.email = f"del_{self.id}: {self.email}"
            self.is_active = False
            self.save()
            super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.user_name = str(self.user_name).title()
        self.email = str(self.email).lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_name}"

    @property
    def get_name(self):
        return f"{self.user_name}"
    
    @staticmethod
    def update_last_checkin(user):
        """
        Update the last check in time for the user when they checkin successfully.
        """
        user.last_checkin = timezone.now()
        user.save(update_fields=['last_checkin'])

    class Meta:
        """
        Meta class for ordering the user objects by their IDs in descending order.
        """
        ordering = ["-id"]
