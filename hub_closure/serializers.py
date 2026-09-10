from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from hub_closure.models import HubClosureDate
from subscription.models import Subscription

MAX_RETROACTIVE_DAYS = 30


class HubClosureDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HubClosureDate
        fields = ['id', 'date', 'reason', 'is_processed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_processed', 'created_at', 'updated_at']

    def validate_date(self, value):
        earliest_allowed = timezone.now().date() - timedelta(days=MAX_RETROACTIVE_DAYS)
        if value < earliest_allowed:
            raise serializers.ValidationError(
                f"Closure dates can only be added up to {MAX_RETROACTIVE_DAYS} days in the past."
            )
        if HubClosureDate.objects.filter(date=value).exists():
            raise serializers.ValidationError("This date has already been marked as closed.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            closure = HubClosureDate.objects.create(**validated_data)
            extend_open_subscriptions_for_closure_date(closure.date)
        return closure


def extend_open_subscriptions_for_closure_date(closure_date):
    """
    Extend every currently open subscription whose active window contains
    `closure_date` by one day, so the closure doesn't eat into the member's
    paid-for 7-day/30-day access. Applies retroactively: a closure day added
    after the fact still extends any subscription that was open on that day
    (i.e. the closure date falls within [created_at date, expiry date]).

    Only ACTIVE (30-day) and PARTIAL_ACTIVE (7-day) subscriptions are
    touched - PENDING has no window yet, and EXPIRED/EXPIRED_PARTIAL/FAILED
    are terminal and shouldn't be revived by a closure day.
    """
    active_subs = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE,
        expires_at__isnull=False,
        created_at__date__lte=closure_date,
        expires_at__date__gte=closure_date,
    )
    for sub in active_subs:
        sub.expires_at = sub.expires_at + timedelta(days=1)
        sub.save()

    partial_subs = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE,
        partial_expires_at__isnull=False,
        created_at__date__lte=closure_date,
        partial_expires_at__date__gte=closure_date,
    )
    for sub in partial_subs:
        sub.partial_expires_at = sub.partial_expires_at + timedelta(days=1)
        sub.save()
