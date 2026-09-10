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

def _resolve_amount(plan, installment_number, amount_override=None):
    if amount_override is not None:
        return amount_override
    if plan.is_paid_in_installment:
        return plan.installment_price
    return plan.price


def initiate_paystack_payment(user, plan, subscription, installment_number=None, amount=None):
    """
    Initialize a Paystack transaction for either a member subscription
    payment or a non-member hourly booking. `amount` is required for
    non-member bookings (hours * hourly rate, computed by the caller since
    hours varies per booking) and optional for member plans (derived from
    the plan's price/installment_price when not given).
    """
    paystack_reference = str(uuid.uuid4())
    amount = _resolve_amount(plan, installment_number, amount)

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
    metadata = {
        "user_id": str(user.id),
        "subscription_id": str(subscription.id),
        "payment_id": str(payment.id),
        "payment_type": "member" if plan.is_member_only else "non_member",
        "installment_number": installment_number or "",
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


def record_offline_payment(user, plan, subscription, installment_number=None, amount=None):
    """
    Record a cash/offline payment taken by an admin on a user's behalf.
    Mirrors initiate_paystack_payment but skips Paystack entirely: the
    Payment is created as already Success, and the same success handler
    used by the webhook is invoked immediately so the resulting
    subscription state (7-day partial / 30-day active / non-member active)
    is identical to what an online payment would produce.
    """
    amount = _resolve_amount(plan, installment_number, amount)

    payment = Payment.objects.create(
        user=user,
        subscription=subscription,
        amount=amount,
        payment_type=Payment.PaymentType.MEMBER_MONTHLY if plan.is_member_only else Payment.PaymentType.NON_MEMBER_HOURLY,
        payment_status=Payment.PaymentStatus.PENDING,
        installment_number=installment_number,
        paystack_reference=f"offline-{uuid.uuid4()}",
    )

    if plan.is_member_only:
        handle_member_success_payment(subscription.id, payment.id)
    else:
        handle_non_member_success_payment(subscription.id, payment.id)

    payment.refresh_from_db()
    return payment

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