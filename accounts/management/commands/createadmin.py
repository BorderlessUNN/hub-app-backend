from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Creates a new admin user (max 2 allowed)'

    def add_arguments(self, parser):
        parser.add_argument('admin_name', type=str, help='Name of the admin')
        parser.add_argument('email', type=str, help='Email address')
        parser.add_argument('password', type=str, help='Password')

    def handle(self, *args, **options):
        admin_name = options['admin_name']
        email = options['email']
        password = options['password']

        try:
            admin = CustomUser.objects.create_admin(
                user_name=admin_name,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin: {admin.email}'))
        except Exception as e:
            raise CommandError(f'Error creating admin: {e}')
