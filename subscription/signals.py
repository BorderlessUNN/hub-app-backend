from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from subscription.models import Subscription
from hub_closure.models import HubClosureDate
from django.utils import timezone
from django.db import transaction
from django.db.models import F

@receiver(post_save, sender=HubClosureDate)
def update_subscriptions_expiry_date(sender, instance, created, **kwargs):
    if created and not instance.is_processed and not instance.is_closed():
        with transaction.atomic():
            Subscription.objects.filter(status=Subscription.SubscriptionStatus.ACTIVE
            , expires_at__gte=instance.date).update(expires_at=F('expires_at') + timezone.timedelta(days=1))
            Subscription.objects.filter(status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE
            , partial_expires_at__gte=instance.date).update(partial_expires_at=F('partial_expires_at') + timezone.timedelta(days=1))
            
            HubClosureDate.objects.filter(id=instance.id).update(is_processed=True)


@receiver(post_delete, sender=HubClosureDate)
def reset_subscriptions_expiry_date(sender, instance, **kwargs):
    if instance.is_processed and not instance.is_closed():
        with transaction.atomic():
            Subscription.objects.filter(status=Subscription.SubscriptionStatus.ACTIVE
            , expires_at__gte=instance.date).update(expires_at=F('expires_at') - timezone.timedelta(days=1))
            
            Subscription.objects.filter(status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE
            , partial_expires_at__gte=instance.date).update(partial_expires_at=F('partial_expires_at') - timezone.timedelta(days=1))
            
            HubClosureDate.objects.filter(id=instance.id).update(is_processed=False)
