from django.db import models

class Member(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

class Guest(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    payment_confirmed = models.BooleanField(default=False)

class Seat(models.Model):
    seat_number = models.CharField(max_length=10, unique=True)
    is_available = models.BooleanField(default=True)

class Booking(models.Model):
    email = models.EmailField()
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
