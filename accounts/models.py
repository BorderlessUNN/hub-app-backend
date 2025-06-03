from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
from django.db import models
from django.utils import timezone
from django.db import transaction

from helpers.models import BaseModel


class CustomUserManager(UserManager):
    """
    Custom user manager that extends Django's built-in UserManager.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a regular User with the given email and password.
        """
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, BaseModel):
    """
    Custom user model that extends Django's built-in AbstractUser.

    """
    # Exclude unnecessary fields from the abstract user model
    username = None
    first_name = None
    last_name = None
    is_staff = None
    date_joined = None
    last_login = None
    is_superuser = None
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  # Specify a custom related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Specify a custom related_name
        blank=True
    )
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

    USERNAME_FIELD = 'email'  # Use email as the field for authentication
    REQUIRED_FIELDS = ['email']
    objects = CustomUserManager()
    
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
