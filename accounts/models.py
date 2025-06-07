from django.db import models
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from helpers.models import BaseModel


class CustomMember(BaseModel):
    """
    Custom member model
    """
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
    is_member = models.BooleanField(default=True)
  
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


class CustomAdminManager(models.Manager):
    def create_admin(self, admin_name, email, password, **extra_fields):
        if self.model.objects.count() >= 2:
            raise ValidationError("Maximum number of admins (2) already exists.")

        email = email.lower()
        password = make_password(password)

        admin = self.model(
            admin_name=admin_name,
            email=email,
            password=password,
            **extra_fields
        )
        admin.full_clean()
        admin.save(using=self._db)
        return admin


class CustomAdmin(BaseModel):
    """
    Custom admin model
    """
    admin_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "An admin with this email already exists."
        }
    )
    password = models.CharField(max_length=128, verbose_name='password')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomAdminManager()

    def save(self, *args, **kwargs):
        self.email = str(self.email).lower()

        # Hash the password if it's not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])