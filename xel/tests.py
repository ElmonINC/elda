from django.test import TestCase
from django.contrib.auth.models import User
from .models import ExcelFile, NameEntry

# Create your tests here.

class XelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(username='admin', password='admin123')

    def test_search_name(self):
        self.client.login(username='testuser', password='12345')
        excel_file = ExcelFile.objects.create(file='test.xlsx')
        NameEntry.objects.create(excel_file=excel_file, first_name='John', last_name='Doe', status='Active')
        response = self.client.post('/xel/search/', {'first_name': 'John', 'last_name': 'Doe'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')