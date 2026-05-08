import uuid
from payments.models import Payment
import requests
from django.conf import settings
from accounts.models import CustomUser
from payments.models import Plans
from subscription.models import Subscription
from django.utils import timezone
from datetime import timedelta
from hub_closure.models import HubClosureDate

def initiate_paystack_payment(user, plan, subscription, installment_number=None):
    paystack_reference = str(uuid.uuid4())
    if plan.is_paid_in_installment:
        amount = plan.installment_price
    else:
        amount = plan.price
    
    payment_type = Payment.PaymentType.MEMBER_MONTHLY if plan.is_member_only else Payment.PaymentType.NON_MEMBER_HOURLY
    payment = Payment.objects.create(
        user=user,
        subscription=subscription,
        amount=amount,
        payment_type=payment_type,
        payment_status=Payment.PaymentStatus.PENDING,
        installment_number=installment_number,
        paystack_reference=paystack_reference
    )
    print(payment)
    metadata = {
        "user_id": str(user.id),
        "subscription_id": str(subscription.id),
        "payment_id": str(payment.id),
    }
    paystack_url = f"https://api.paystack.co/transaction/initialize"
    payload = {
        "amount":amount * 100,
        "email": user.email,
        "reference": paystack_reference,
        "metadata": metadata
    }
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    paystack_response = requests.post(paystack_url, headers=headers, json=payload)
    return paystack_response.json()

def handle_member_success_payment(subscription_id, payment_id):
    subscription = Subscription.objects.get(id=subscription_id)
    payment = Payment.objects.get(id=payment_id)
    payment.payment_status = Payment.PaymentStatus.SUCCESS
    payment.save()
    today = timezone.now().date()
    
    
    if payment.installment_number == Payment.InstallmentNumber.ONE:
        hub_closure_dates = HubClosureDate.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=7),
        ).count()
        subscription.status = Subscription.SubscriptionStatus.PARTIAL_ACTIVE
        subscription.partial_expires_at =  timezone.now() + timedelta(days= 7 + hub_closure_dates)

    elif payment.installment_number == Payment.InstallmentNumber.TWO:
        subscription.status = Subscription.SubscriptionStatus.ACTIVE
        subscription.partial_expires_at = None
        used_days = today - subscription.created_at.date()
        hub_closure_dates = HubClosureDate.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=30 - used_days.days),
        ).count()
        subscription.expires_at = timezone.now() + timedelta(days=30 + hub_closure_dates) - used_days
    else:
        hub_closure_dates = HubClosureDate.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=30),
        ).count()
        subscription.status = Subscription.SubscriptionStatus.ACTIVE
        subscription.expires_at = timezone.now() + timedelta(days=30 + hub_closure_dates)
    subscription.save()
    return payment

def handle_non_member_success_payment(subscription_id, payment_id):
    subscription = Subscription.objects.get(id=subscription_id)
    payment = Payment.objects.get(id=payment_id)
    payment.payment_status = Payment.PaymentStatus.SUCCESS
    payment.save()
    subscription.status = Subscription.SubscriptionStatus.ACTIVE
    subscription.save()
    print(payment)
    return payment

def handle_failed_payment(subscription_id, payment_id):
    subscription = Subscription.objects.get(id=subscription_id)
    payment = Payment.objects.get(id=payment_id)
    payment.payment_status = Payment.PaymentStatus.FAILED
    payment.save()
    subscription.status = Subscription.SubscriptionStatus.FAILED
    subscription.save()
    return payment