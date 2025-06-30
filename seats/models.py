from django.db import models

from helpers.models import BaseModel


class Seat(BaseModel):
    seat_number = models.IntegerField(unique=True, null=False)

    class Meta:
        ordering = ['seat_number']


class SeatBookings(BaseModel):
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='seat_bookings'
    )
    seat = models.ForeignKey(
        'seats.Seat',
        on_delete=models.CASCADE,
        related_name='seat_bookings'
    )
    checkin_at = models.DateTimeField(auto_now_add=True)
    checkout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
