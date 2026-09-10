import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from seats.models import Seat

class Command(BaseCommand):
    help = "Populates the database with one Super Admin user, seat records, and payment plans."

    def handle(self, *args, **kwargs):
        # 1. Create an admin account (optional; requires env vars)
        admin_email = os.getenv("CUSTOM_ADMIN_EMAIL")
        admin_name = os.getenv("CUSTOM_ADMIN_NAME")
        admin_password = os.getenv("CUSTOM_ADMIN_PASSWORD")

        if not all([admin_email, admin_name, admin_password]):
            self.stdout.write(self.style.WARNING(
                "Skipping admin creation: set CUSTOM_ADMIN_EMAIL, CUSTOM_ADMIN_NAME, and CUSTOM_ADMIN_PASSWORD"
            ))
        else:
            try:
                if not CustomUser.objects.filter(email=admin_email).exists():
                    CustomUser.objects.create_admin(
                        user_name=admin_name,
                        email=admin_email,
                        password=admin_password,
                        admin_role=CustomUser.AdminRole.SUPER,
                    )
                    self.stdout.write(self.style.SUCCESS("Super Admin user created"))
                else:
                    self.stdout.write(self.style.WARNING("Admin user already exists"))
            except ValidationError as e:
                self.stdout.write(self.style.WARNING(f"Admin not created: {e}"))

        # 2. Create 10 seat records
        seat_count = 10
        created_seats = 0
        for i in range(1, seat_count + 1):
            _, created = Seat.objects.get_or_create(seat_number=i)
            if created:
                created_seats += 1
        self.stdout.write(self.style.SUCCESS(f"{created_seats} seats created"))

        # 3. Payment plans - delegated to `seed_plans`, the single source of
        # truth for plan pricing (see payments/management/commands/seed_plans.py).
        call_command("seed_plans")
