from django.db import models
from helpers.models import BaseModel
from accounts.models import CustomUser
from django.utils.text import slugify
from subscription.models import Subscription

class Plans(BaseModel):
    name = models.CharField(max_length=20)
    price = models.IntegerField(null=False, blank=False,)
    hours = models.IntegerField(null=True, blank=True)
    slug  = models.SlugField( blank=True, null=True)
    is_member_only = models.BooleanField(default=True)
    is_paid_in_installment = models.BooleanField(null=True, blank=True)
    installment_price = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.slug

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
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    amount = models.BigIntegerField(null = True, blank = True)
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices, blank = False, null = False, default=PaymentType.MEMBER_MONTHLY)
    payment_status = models.CharField(max_length=30, choices=PaymentStatus.choices, blank = False, null = False, default=PaymentStatus.PENDING)
    paystack_reference = models.CharField(max_length=100, null = True, blank = True)
    installment_number = models.CharField(max_length=30, choices=InstallmentNumber.choices, blank = True, null = True)


