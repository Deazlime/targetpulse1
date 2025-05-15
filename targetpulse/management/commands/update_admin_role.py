from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from targetpulse.models import UserProfile

class Command(BaseCommand):
    help = 'Updates the admin user role to developer'

    def handle(self, *args, **options):
        try:
            admin_user = User.objects.get(username='admin')
            profile = UserProfile.objects.get(user=admin_user)
            profile.role = 'developer'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {admin_user.username}'s role to developer"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found'))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user profile not found')) 