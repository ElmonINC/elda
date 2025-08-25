from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from xel.models import UserProfile
import os

class Command(BaseCommand):
    help = 'Creates an initial admin user if none exists'

    def handle(self, *args, **options):
        if UserProfile.objects.filter(is_admin=True).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        try:
            username = os.environ['ADMIN_USERNAME']
            email = os.environ['ADMIN_EMAIL']
            password = os.environ['ADMIN_PASSWORD']
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Environment variable {e} not set"))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        UserProfile.objects.create(user=user, is_admin=True)
        self.stdout.write(self.style.SUCCESS(f"Admin account '{username}' created successfully"))