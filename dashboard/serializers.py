from rest_framework import serializers
from django.utils.timezone import now
from datetime import timedelta
from seats.models import Seat
from seats.models import SeatBookings
from accounts.models import CustomUser

class CheckInStatsSerializer(serializers.Serializer):
    checked_in_count = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    checked_in_users = serializers.SerializerMethodField()

    def get_checked_in_users(self, obj):
        return self._get_today_checkins()

    def get_checked_in_count(self, obj):
        return len(self._get_today_checkins())

    def get_available_seats(self, obj):
        return self._get_available_seats()

    def _get_today_checkins(self):
        today = now().date()
        checkins = SeatBookings.objects.filter(
            checkin_at__date=today,
            is_active=True
        ).select_related('user', 'seat')

        return [
            {
                "name": booking.user.user_name,
                "email": booking.user.email,
                "seat_number": booking.seat.seat_number
            }
            for booking in checkins
        ]

    def _get_available_seats(self):
        total_seats = Seat.objects.count()
        booked_seats = Seat.objects.filter(is_booked=True).count()
        return total_seats - booked_seats

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.SerializerMethodField()
    member_percentage = serializers.SerializerMethodField()
    non_member_percentage = serializers.SerializerMethodField()

    def get_total_users(self, obj):
        return self._get_user_stats()['total']

    def get_member_percentage(self, obj):
        return self._get_user_stats()['member_percentage']

    def get_non_member_percentage(self, obj):
        return self._get_user_stats()['non_member_percentage']

    def _get_user_stats(self):
        # Get months from context or default to 1
        months = self.context.get('months', 1)
        try:
            months = int(months)
            if months <= 0:
                months = 1
        except (ValueError, TypeError):
            months = 1

        since = now() - timedelta(days=months * 30)

        user_ids = (
            SeatBookings.objects
            .filter(checkin_at__gte=since)
            .values_list('user_id', flat=True)
            .distinct()
        )

        users = CustomUser.objects.filter(id__in=user_ids)
        total = users.count()

        if total == 0:
            return {
                "total": 0,
                "member_percentage": 0.0,
                "non_member_percentage": 0.0
            }

        member_count = users.filter(is_member=True).count()
        non_member_count = total - member_count

        return {
            "total": total,
            "member_percentage": round((member_count / total) * 100, 2),
            "non_member_percentage": round((non_member_count / total) * 100, 2)
        }
