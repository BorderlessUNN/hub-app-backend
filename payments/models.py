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
    is_member_only = models.BooleanField(null=False, blank=False,)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Payment(BaseModel):
    class PaymentType(models.TextChoices):
        MEMBER_MONTHLY = 'Member Monthly', 'Member Monthly'
        NON_MEMBER_HOURLY = 'Non Member Hourly', 'Non Member Hourly'

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        SUCCESS = 'Success', 'Success'
        FAILED = 'Failed', 'Failed'
    class InstallmentNumber(models.TextChoices):
        ONE = '1', 'One'
        TWO = '2', 'Two'
    user_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    plan_id = models.ForeignKey(
        Plans,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.BigIntegerField(null=False, blank=False)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices, blank = False, null = False)
    payment_status = models.CharField(max_length=30, choices=PaymentStatus.choices, blank = False, null = False)
    paystack_reference = models.CharField(max_length=100, null = False, blank = False)
    installment_number = models.CharField(max_length=30, choices=InstallmentNumber.choices, blank = False, null = False)


