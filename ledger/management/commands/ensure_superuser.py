from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create a superuser from environment variables if it doesn't exist."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                "Superuser env vars missing. "
                "Required: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD"
            ))
            return

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists. Skipping creation."))
            return

        # Add any extra required fields for your custom User model here
        extra_fields = {
            "is_staff": True,
            "is_superuser": True,
        }
        # Example if your model requires 'full_name':
        # extra_fields["full_name"] = os.getenv("DJANGO_SUPERUSER_FULL_NAME", "Admin")

        user = User.objects.create_user(username=username, email=email, password=password, **extra_fields)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
