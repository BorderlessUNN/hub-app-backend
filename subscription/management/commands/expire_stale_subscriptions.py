from django.core.management.base import BaseCommand
from django.utils import timezone

from subscription.models import Subscription


class Command(BaseCommand):
    help = (
        "Flip any subscription whose window has passed to its terminal state. "
        "Reports always compute status live, so this is only a housekeeping "
        "sweep to keep stored `status` values fresh - safe to run on a cron."
    )

    def handle(self, *args, **options):
        now = timezone.now()

        expired = Subscription.objects.filter(
            status=Subscription.SubscriptionStatus.ACTIVE,
            expires_at__isnull=False,
            expires_at__lt=now,
        )
        expired_count = 0
        for sub in expired:
            # Subscription.save() flips ACTIVE -> EXPIRED when expires_at has passed.
            sub.save()
            expired_count += 1

        expired_partial = Subscription.objects.filter(
            status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE,
            partial_expires_at__isnull=False,
            partial_expires_at__lt=now,
        )
        expired_partial_count = 0
        for sub in expired_partial:
            sub.save()
            expired_partial_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Expired {expired_count} active and {expired_partial_count} partial-active subscriptions."
        ))
