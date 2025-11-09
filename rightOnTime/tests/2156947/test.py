from django.test import TestCase
from administrator.models import Administrator

class AdministratorModelTest(TestCase):
    def create_admin_test(self):
        admin = Administrator.objects.create_superuser(
            username = 'admin1',
            email = 'nicole@ejemplo.com',
            password = 'Nicolita123.',
            id_administrator = 'ADM001',
            phone_number = 301564897,
            first_name = 'Nicole',
            last_name = 'Narvaez',
            is_staff = True
        )
        self.assertIsInstance(admin, Administrator)
        self.assertEqual(admin.username, 'admin1')
        self.assertEqual(admin.email, 'nicole@ejemplo.com')
        self.assertTrue(admin.check_password('Nicolita123.'))
        self.assertEqual(admin.id_administrator, 'ADM001')
        self.assertEqual(admin.phone_number, 301564897)     