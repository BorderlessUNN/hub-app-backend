from rest_framework import serializers
from django.utils.timezone import now
from seats.models import Seat
from seats.models import SeatBookings

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
