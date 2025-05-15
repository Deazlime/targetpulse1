from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from targetpulse.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a manager account'

    def handle(self, *args, **options):
        try:
            # Create the user
            user = User.objects.create_user(
                username='manager',
                password='manager123',  # Default password
                email='manager@example.com'
            )
            
            # Create the user profile with manager role
            profile = UserProfile.objects.create(
                user=user,
                first_name='Manager',
                last_name='User',
                role='manager'
            )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created manager account with username: {user.username}"))
            self.stdout.write(self.style.WARNING("Default password is: manager123"))
            self.stdout.write(self.style.WARNING("Please change the password after first login"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating manager account: {str(e)}')) 