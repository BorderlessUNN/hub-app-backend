from django.utils import timezone
from datetime import timedelta
from payments.models import Payment
from hub_closure.models import HubClosureDate
from subscription.models import Subscription

def handle_admin_assigned_member_subscription(subscription, installment_number = None):
    today = timezone.now().date()
    
    
    if installment_number == Payment.InstallmentNumber.ONE:
        hub_closure_dates = HubClosureDate.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=7),
        ).count()
        subscription.status = Subscription.SubscriptionStatus.PARTIAL_ACTIVE
        subscription.partial_expires_at =  timezone.now() + timedelta(days= 7 + hub_closure_dates)

    elif installment_number == Payment.InstallmentNumber.TWO:
        print(Payment.InstallmentNumber.TWO)
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
    return subscription


def handle_non_member_is_admin_assigned_subscription(subscription):
    subscription.status = Subscription.SubscriptionStatus.ACTIVE
    subscription.save()
    return subscription