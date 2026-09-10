from django.db import models
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
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
        extra_fields.setdefault('admin_role', CustomUser.AdminRole.SUPER)
        return self.create_user(email, password, **extra_fields)

    def create_admin(self, user_name, email, password, admin_role=None, **extra_fields):
        """
        Admin creation logic.

        Every admin account (Super or Staff) is a Django is_staff + is_superuser
        account, so existing admin-only endpoints keep working unchanged for
        both tiers. `admin_role` distinguishes Super Admin from Staff Admin for
        the tier-specific permission checks. There is no ceiling on the number
        of admin accounts, but at least one active Super Admin must always
        exist (enforced on deactivation, not on creation).
        """
        admin_role = admin_role or CustomUser.AdminRole.STAFF
        if admin_role not in CustomUser.AdminRole.values:
            raise ValidationError("Invalid admin role.")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['admin_role'] = admin_role
        return self.create_user(
            email=email,
            password=password,
            user_name=user_name,
            **extra_fields
        )

class CustomUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Final Unified Model: All users login via Email.
    """
    class AdminRole(models.TextChoices):
        SUPER = 'super', 'Super Admin'
        STAFF = 'staff', 'Staff Admin'

    user_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        error_messages={"unique": "A user with this email already exists."}
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)

    # Club Specific Info
    department = models.CharField(max_length=200, blank=True, null =True)
    tech_stack = models.CharField(max_length=200, blank=True, null =True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Flags
    is_member = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) #
    is_superuser = models.BooleanField(default=False)
    admin_role = models.CharField(
        max_length=10, choices=AdminRole.choices, blank=True, null=True,
        help_text="Only set for admin accounts (is_superuser=True). Null for members/non-members.",
    )
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    # Django Standards for Email Auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    class Meta:
        ordering = ["-id"]
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            # Only members are required to have a unique phone number.
            # Non-members are tracked separately and may share/lack numbers.
            models.UniqueConstraint(
                fields=['phone_number'],
                condition=Q(is_member=True),
                name='unique_member_phone_number',
            ),
        ]

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

    @property
    def is_super_admin(self):
        return self.is_superuser and self.admin_role == self.AdminRole.SUPER
