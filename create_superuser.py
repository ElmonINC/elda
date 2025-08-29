# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elda.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "elmon")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "igwesmsn@gmail.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Dip1tip2Dwaka@#elW")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created ✅")
else:
    u = User.objects.get(username=username)
    u.is_staff = True
    u.is_superuser = True
    u.set_password(password)  # reset in case old password was wrong
    u.save()
    print("Superuser already exists, updated ✅")
