import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'targetpulse.settings')
django.setup()

from django.contrib.auth.models import User
from targetpulse.models import UserProfile

# Get the admin user and their profile
admin_user = User.objects.get(username='admin')
profile = UserProfile.objects.get(user=admin_user)

# Update the role to developer
profile.role = 'developer'
profile.save()

print(f"Successfully updated {admin_user.username}'s role to developer") 