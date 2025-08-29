import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elda.settings')
django.setup()

User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'elmon')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'igwesmsn@gmail.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'Dip1tip2Dwaka@#elW')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")