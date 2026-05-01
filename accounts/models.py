from django.db import models
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from helpers.models import BaseModel

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Base user creation logic.
        """
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            # Members created by admin won't have a password until they set it
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    # def create_admin(self, user_name, email, password, **extra_fields):
    #     """
    #     Admin creation logic with the strict 2-admin limit.
    #     """
    #     if self.filter(is_staff=True).count() >= 2:
    #         raise ValidationError("Maximum number of admins (2) already exists.")

    #     extra_fields.setdefault('is_staff', True)
    #     return self.create_user(
    #         email=email, 
    #         password=password, 
    #         user_name=user_name, 
    #         **extra_fields
    #     )

class CustomUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Final Unified Model: All users login via Email.
    """
    user_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        error_messages={"unique": "A user with this email already exists."}
    )
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Club Specific Info
    department = models.CharField(max_length=200, blank=True, null =True)
    tech_stack = models.CharField(max_length=200, blank=True, null =True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Flags
    is_member = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) #
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    # Django Standards for Email Auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    class Meta:
        ordering = ["-id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        self.user_name = str(self.user_name).title()
        self.email = str(self.email).lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Soft delete with unique constraint safety"""
        with transaction.atomic():
            self.email = f"del_{self.id}_{self.email}"
            self.is_active = False
            self.save()

    def __str__(self):
        return self.email

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

    @property
    def get_name(self):
        return self.user_name