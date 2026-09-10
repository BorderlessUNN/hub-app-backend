from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Creates a new admin user (Super Admin by default; pass --role staff for a Staff Admin)'

    def add_arguments(self, parser):
        parser.add_argument('admin_name', type=str, help='Name of the admin')
        parser.add_argument('email', type=str, help='Email address')
        parser.add_argument('password', type=str, help='Password')
        parser.add_argument(
            '--role',
            type=str,
            default=CustomUser.AdminRole.SUPER,
            choices=CustomUser.AdminRole.values,
            help='Admin tier: super (default) or staff',
        )

    def handle(self, *args, **options):
        admin_name = options['admin_name']
        email = options['email']
        password = options['password']
        admin_role = options['role']

        try:
            admin = CustomUser.objects.create_admin(
                user_name=admin_name,
                email=email,
                password=password,
                admin_role=admin_role,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {admin.get_admin_role_display()}: {admin.email}'
            ))
        except Exception as e:
            raise CommandError(f'Error creating admin: {e}')
