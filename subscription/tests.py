from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from hub_closure.serializers import extend_open_subscriptions_for_closure_date
from payments.models import Plans
from payments.services import record_offline_payment
from subscription.models import Subscription
from subscription.serializers import MemberSubscriptionSerializer


class SubscriptionGuardTests(TestCase):
    def setUp(self):
        self.member = CustomUser.objects.create_user(
            email="member@example.com", user_name="Member", is_member=True,
            phone_number="+2348012345678",
        )
        self.full_plan = Plans.objects.create(
            name="Member Full", slug="member-full", price=5000,
            is_member_only=True, is_paid_in_installment=False,
        )

    def test_blocks_second_open_subscription(self):
        Subscription.objects.create(
            user=self.member, plan=self.full_plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
        )
        serializer = MemberSubscriptionSerializer(data={
            "user_id": str(self.member.id),
            "plan_id": str(self.full_plan.id),
            "is_admin_assigned": False,
        })
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_allows_new_subscription_after_expired_partial(self):
        # A terminal expired_partial must not block a fresh start.
        Subscription.objects.create(
            user=self.member, plan=self.full_plan,
            status=Subscription.SubscriptionStatus.EXPIRED_PARTIAL,
        )
        serializer = MemberSubscriptionSerializer(data={
            "user_id": str(self.member.id),
            "plan_id": str(self.full_plan.id),
            "is_admin_assigned": False,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)


class OfflinePaymentTests(TestCase):
    def setUp(self):
        self.member = CustomUser.objects.create_user(
            email="member@example.com", user_name="Member", is_member=True,
            phone_number="+2348012345678",
        )
        self.full_plan = Plans.objects.create(
            name="Member Full", slug="member-full", price=5000,
            is_member_only=True, is_paid_in_installment=False,
        )

    def test_full_offline_payment_activates_30_days(self):
        sub = Subscription.objects.create(user=self.member, plan=self.full_plan)
        payment = record_offline_payment(self.member, self.full_plan, sub)
        sub.refresh_from_db()
        self.assertEqual(sub.status, Subscription.SubscriptionStatus.ACTIVE)
        self.assertIsNotNone(sub.expires_at)
        # ~30 days out (allow a small delta for execution time).
        self.assertGreater(sub.expires_at, timezone.now() + timedelta(days=29))
        self.assertEqual(payment.payment_status, "Success")


class InstallmentFlowTests(TestCase):
    def setUp(self):
        self.member = CustomUser.objects.create_user(
            email="member@example.com", user_name="Member", is_member=True,
            phone_number="+2348012345678",
        )
        self.installment_plan = Plans.objects.create(
            name="Member Installment", slug="member-installment", price=5000,
            is_member_only=True, is_paid_in_installment=True, installment_price=2500,
        )

    def test_first_installment_gives_partial_7_days(self):
        sub = Subscription.objects.create(user=self.member, plan=self.installment_plan)
        record_offline_payment(self.member, self.installment_plan, sub, installment_number="1")
        sub.refresh_from_db()
        self.assertEqual(sub.status, Subscription.SubscriptionStatus.PARTIAL_ACTIVE)
        self.assertIsNotNone(sub.partial_expires_at)

    def test_second_installment_completes_to_active(self):
        sub = Subscription.objects.create(user=self.member, plan=self.installment_plan)
        record_offline_payment(self.member, self.installment_plan, sub, installment_number="1")
        record_offline_payment(self.member, self.installment_plan, sub, installment_number="2")
        sub.refresh_from_db()
        self.assertEqual(sub.status, Subscription.SubscriptionStatus.ACTIVE)
        self.assertIsNone(sub.partial_expires_at)
        self.assertIsNotNone(sub.expires_at)


class ClosureExtensionTests(TestCase):
    def setUp(self):
        self.member = CustomUser.objects.create_user(
            email="member@example.com", user_name="Member", is_member=True,
            phone_number="+2348012345678",
        )
        self.full_plan = Plans.objects.create(
            name="Member Full", slug="member-full", price=5000,
            is_member_only=True, is_paid_in_installment=False,
        )

    def test_closure_within_window_extends_active_subscription(self):
        sub = Subscription.objects.create(
            user=self.member, plan=self.full_plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=20),
        )
        original_expiry = sub.expires_at
        # A closure day 5 days from now falls inside the active window.
        closure_date = (timezone.now() + timedelta(days=5)).date()
        extend_open_subscriptions_for_closure_date(closure_date)
        sub.refresh_from_db()
        self.assertEqual(sub.expires_at.date(), (original_expiry + timedelta(days=1)).date())

    def test_closure_outside_window_does_not_extend(self):
        sub = Subscription.objects.create(
            user=self.member, plan=self.full_plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
            expires_at=timezone.now() + timedelta(days=5),
        )
        original_expiry = sub.expires_at
        # A closure day 20 days out is beyond this subscription's expiry.
        closure_date = (timezone.now() + timedelta(days=20)).date()
        extend_open_subscriptions_for_closure_date(closure_date)
        sub.refresh_from_db()
        self.assertEqual(sub.expires_at, original_expiry)
