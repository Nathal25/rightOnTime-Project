from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from administrator.models import Administrator

# Test case class for administrator login functionality
class AdminLoginTestCase(APITestCase):
    """
    Set up method that runs before each test.
    Creates test users for authentication testing.
    """
    def setUp(self):
        # Create an administrator user (staff member)
        self.admin_user = Administrator.objects.create_user(
            username='admin1',
            email='nicole@ejemplo.com',
            password='Nicolita123.',
            id_administrator='ADM001',
            phone_number=301564897,
            first_name='Nicole',
            last_name='Narvaez',
            is_staff=True # This flag marks the user as staff/admin
        )

        # Create a regular user (non-staff)
        self.normal_user = Administrator.objects.create_user(
            username='user1',
            password='userpass123',
            email='user1@example.com',
            id_administrator='EMP001',
            phone_number=3123456790,
            is_staff=False, # This user is NOT an administrator
        )

        # Store the URL endpoint for admin login
        self.url = reverse('admin-login')
    
    """
    Test that verifies a staff user can successfully login 
    and receive JWT tokens (access and refresh).
    """
    def test_admin_can_login_and_receive_tokens(self):
        # Send POST request with admin credentials
        response = self.client.post(self.url, {
            'username': 'admin1',
            'password': 'Nicolita123.'
        }, format='json')

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains an access token
        self.assertIn('access', response.data)

        # Check that the response contains a refresh token
        self.assertIn('refresh', response.data)
    
    """
    Test that verifies a non-staff user CANNOT login.
    The login should fail for users without staff privileges.
    """
    def test_non_admin_cannot_login(self):
        # Send POST request with non-admin credentials
        response = self.client.post(self.url, {
            'username': 'user1',
            'password': 'userpass123'
        }, format='json')

        # Check that the response status is NOT 200 OK (login should fail)
        # The serializer, it raises an Exception
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains error details
        self.assertIn('detail', response.data)