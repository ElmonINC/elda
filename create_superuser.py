# create_superuser.py
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elda.settings")
django.setup()

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "elmon")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "igwesmsn@example.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Dip1tip2Dwaka@#elW")

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print(f"Superuser {username} already exists. Resetting password...")
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
