from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework.views import APIView

from accounts.models import CustomUser
from accounts.permissions import IsAdminUser, IsSuperAdminUser
from check_in.models import CheckIn
from helpers.responses import CustomResponse
from payments.models import Payment
from subscription.models import Subscription


# Members within this many days of their partial (7-day) cutoff are flagged
# so front-desk staff can nudge them to complete the second installment.
PARTIAL_WARNING_DAYS = 2


class PaymentsReportView(APIView):
    """
    Revenue report for a given month (Super Admin only). Counts and totals
    for full payments, installment payments, and completed installment pairs.
    Query param: ?month=YYYY-MM (defaults to the current month).
    """
    permission_classes = [IsSuperAdminUser]

    def get(self, request):
        month_str = request.query_params.get('month')
        today = timezone.now()
        if month_str:
            try:
                year, month = map(int, month_str.split('-'))
                period_start = timezone.make_aware(datetime(year, month, 1))
            except (ValueError, TypeError):
                return CustomResponse(valid=False, msg="Invalid month format, expected YYYY-MM", status=400)
        else:
            period_start = timezone.make_aware(datetime(today.year, today.month, 1))

        # First day of the following month.
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)

        successful = Payment.objects.filter(
            payment_status=Payment.PaymentStatus.SUCCESS,
            created_at__gte=period_start,
            created_at__lt=period_end,
        )

        full_payments = successful.filter(installment_number__isnull=True)
        installment_payments = successful.filter(installment_number__isnull=False)
        first_installments = successful.filter(installment_number=Payment.InstallmentNumber.ONE)
        second_installments = successful.filter(installment_number=Payment.InstallmentNumber.TWO)

        def _agg(qs):
            return {
                "count": qs.count(),
                "total": sum(p.amount or 0 for p in qs),
            }

        data = {
            "month": period_start.strftime('%Y-%m'),
            "full_payments": _agg(full_payments),
            "installment_payments": _agg(installment_payments),
            "first_installments": _agg(first_installments),
            "second_installments": _agg(second_installments),
            # A completed pair = a subscription where the 2nd installment
            # landed this month.
            "completed_installment_pairs": second_installments.count(),
            "grand_total": sum(p.amount or 0 for p in successful),
        }
        return CustomResponse(valid=True, msg="Payments report fetched successfully", data=data)


class UsersByStatusReportView(APIView):
    """
    Lists users grouped by subscription status (Super Admin only): active
    members, partial-access members (with days-to-cutoff), expired members,
    and non-members with remaining time.
    """
    permission_classes = [IsSuperAdminUser]

    def get(self, request):
        now = timezone.now()

        def _user_row(sub, extra=None):
            row = {
                "user_id": str(sub.user.id),
                "name": sub.user.user_name,
                "email": sub.user.email,
                "phone_number": sub.user.phone_number,
                "subscription_id": str(sub.id),
                "status": sub.status,
                "expires_at": sub.expires_at,
                "partial_expires_at": sub.partial_expires_at,
            }
            if extra:
                row.update(extra)
            return row

        active_members = [
            _user_row(sub)
            for sub in Subscription.objects.filter(
                status=Subscription.SubscriptionStatus.ACTIVE, user__is_member=True
            ).select_related('user')
        ]

        partial_members = []
        for sub in Subscription.objects.filter(
            status=Subscription.SubscriptionStatus.PARTIAL_ACTIVE, user__is_member=True
        ).select_related('user'):
            days_left = None
            nearing = False
            if sub.partial_expires_at:
                delta = sub.partial_expires_at - now
                days_left = max(delta.days, 0)
                nearing = timedelta(0) < delta <= timedelta(days=PARTIAL_WARNING_DAYS)
            partial_members.append(_user_row(sub, {
                "days_to_cutoff": days_left,
                "is_nearing_cutoff": nearing,
            }))

        expired_members = [
            _user_row(sub)
            for sub in Subscription.objects.filter(
                status__in=[
                    Subscription.SubscriptionStatus.EXPIRED,
                    Subscription.SubscriptionStatus.EXPIRED_PARTIAL,
                ],
                user__is_member=True,
            ).select_related('user')
        ]

        non_members_with_time = []
        for sub in Subscription.objects.filter(
            status=Subscription.SubscriptionStatus.ACTIVE, user__is_member=False
        ).select_related('user'):
            remaining_seconds = None
            if sub.expires_at:
                remaining_seconds = max(int((sub.expires_at - now).total_seconds()), 0)
            non_members_with_time.append(_user_row(sub, {
                "remaining_seconds": remaining_seconds,
            }))

        data = {
            "active_members": active_members,
            "partial_members": partial_members,
            "expired_members": expired_members,
            "non_members_with_time": non_members_with_time,
        }
        return CustomResponse(valid=True, msg="Users-by-status report fetched successfully", data=data)


class DailyCheckinsReportView(APIView):
    """
    Today's (or a given date's) check-in list, split by member type and
    status - any admin tier can view (front-desk capability). Query param:
    ?date=YYYY-MM-DD (defaults to today, Africa/Lagos).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return CustomResponse(valid=False, msg="Invalid date format, expected YYYY-MM-DD", status=400)
        else:
            target_date = timezone.localtime().date()

        now = timezone.now()
        checkins = CheckIn.objects.filter(
            created_at__date=target_date
        ).select_related('subscription', 'subscription__user')

        active_members = []
        partial_members = []
        expired_users = []
        non_members = []

        for ci in checkins:
            sub = ci.subscription
            user = sub.user
            base = {
                "checkin_id": str(ci.id),
                "user_id": str(user.id),
                "name": user.user_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "start_time": ci.start_time,
                "status": sub.status,
            }

            if not user.is_member:
                remaining_seconds = None
                is_expired = False
                nearing = False
                if ci.expiry_date_time:
                    delta = ci.expiry_date_time - now
                    remaining_seconds = max(int(delta.total_seconds()), 0)
                    is_expired = ci.expiry_date_time < now and ci.end_time is None
                    nearing = timedelta(0) < delta <= timedelta(minutes=30)
                non_members.append({
                    **base,
                    "expiry_date_time": ci.expiry_date_time,
                    "end_time": ci.end_time,
                    "remaining_seconds": remaining_seconds,
                    "is_expired": is_expired,
                    "is_nearing_expiry": nearing,
                })
            elif sub.status == Subscription.SubscriptionStatus.ACTIVE:
                active_members.append(base)
            elif sub.status == Subscription.SubscriptionStatus.PARTIAL_ACTIVE:
                nearing = False
                if sub.partial_expires_at:
                    delta = sub.partial_expires_at - now
                    nearing = timedelta(0) < delta <= timedelta(days=PARTIAL_WARNING_DAYS)
                partial_members.append({
                    **base,
                    "partial_expires_at": sub.partial_expires_at,
                    "is_nearing_cutoff": nearing,
                })
            else:
                expired_users.append(base)

        data = {
            "date": target_date.isoformat(),
            "active_members": active_members,
            "partial_members": partial_members,
            "expired_users": expired_users,
            "non_members": non_members,
        }
        return CustomResponse(valid=True, msg="Daily check-ins report fetched successfully", data=data)
