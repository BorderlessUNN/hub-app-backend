from django.core.management.base import BaseCommand

from payments.models import Plans

# Canonical pricing. Edit these values and re-run `manage.py seed_plans` to
# change pricing without a code deploy - the command upserts by slug, so
# re-running it always brings existing rows in line with what's below.
PLAN_DEFINITIONS = [
    {
        "slug": "member-full",
        "name": "Member Full Monthly",
        "price": 5000,
        "hours": None,
        "is_member_only": True,
        "is_paid_in_installment": False,
        "installment_price": None,
    },
    {
        "slug": "member-installment",
        "name": "Member Installment Monthly",
        "price": 5000,
        "hours": None,
        "is_member_only": True,
        "is_paid_in_installment": True,
        "installment_price": 2500,
    },
    {
        "slug": "non-member-hourly",
        "name": "Non-Member Hourly",
        "price": 400,
        "hours": None,
        "is_member_only": False,
        "is_paid_in_installment": False,
        "installment_price": None,
    },
]


class Command(BaseCommand):
    help = (
        "Seeds/updates the canonical subscription plans (member full, member "
        "installment, non-member hourly rate). Safe to re-run after editing "
        "PLAN_DEFINITIONS in this file to change pricing."
    )

    def handle(self, *args, **options):
        for spec in PLAN_DEFINITIONS:
            slug = spec["slug"]
            defaults = {k: v for k, v in spec.items() if k != "slug"}
            plan, created = Plans.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} plan '{plan.name}' ({slug})"))

        self.stdout.write(self.style.SUCCESS("Plan seeding complete."))
