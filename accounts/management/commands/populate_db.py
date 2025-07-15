import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from accounts.models import CustomAdmin
from seats.models import Seat
from payments.models import Plans

class Command(BaseCommand):
    help = "Populates the database with one CustomAdmin, seat records, and payment plans."

    def handle(self, *args, **kwargs):
        # 1. Create a CustomAdmin account
        admin_email = os.getenv("CUSTOM_ADMIN_EMAIL")
        admin_name = os.getenv("CUSTOM_ADMIN_NAME")
        admin_password = os.getenv("CUSTOM_ADMIN_PASSWORD")

        try:
            if not CustomAdmin.objects.filter(email=admin_email).exists():
                CustomAdmin.objects.create_admin(
                    admin_name=admin_name,
                    email=admin_email,
                    password=admin_password
                )
                self.stdout.write(self.style.SUCCESS("Custom admin created"))
            else:
                self.stdout.write(self.style.WARNING("Custom admin already exists"))
        except ValidationError as e:
            self.stdout.write(self.style.WARNING(f"Admin not created: {e.message}"))

        # 2. Create 10 seat records
        seat_count = 10
        created_seats = 0
        for i in range(1, seat_count + 1):
            _, created = Seat.objects.get_or_create(seat_number=i)
            if created:
                created_seats += 1
        self.stdout.write(self.style.SUCCESS(f"{created_seats} seats created"))

        # 3. Create payment plans
        plans_data = [
            {"name": "Hourly", "price": 500, "hours": 1},
            {"name": "Half Day", "price": 1500, "hours": 4},
            {"name": "Full Day", "price": 3000, "hours": 8},
        ]

        created_plans = 0
        for plan in plans_data:
            _, created = Plans.objects.get_or_create(
                name=plan["name"],
                defaults={
                    "price": plan["price"],
                    "hours": plan["hours"]
                }
            )
            if created:
                created_plans += 1

        self.stdout.write(self.style.SUCCESS(f"{created_plans} plans added"))
