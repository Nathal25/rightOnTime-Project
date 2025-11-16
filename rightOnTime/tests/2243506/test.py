from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from employees.models import Employee
from administrator.models import Administrator
from rest_framework_simplejwt.tokens import RefreshToken


class EmployeesAPITestCase(APITestCase):
    """Test suite for the Employee module endpoints"""

    def setUp(self):
        """Sets up an authenticated admin user and base URL"""
        # Create a real administrator user
        test_password = "test_password"
        self.admin_user = Administrator.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password=test_password,
            id_administrator='ADM001',
            phone_number=3001112233,
            is_staff=True
        )

        # Generate JWT token manually (no need to call /api/token/)
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)

        # Base URL for employee endpoints
        self.url = reverse('employee-list')

    def test_authenticated_admin_can_list_employees(self):
        """Verifies that an authenticated user can list employees"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_list_employees(self):
        """Verifies that an unauthenticated user cannot list employees"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_admin_can_get_employee_detail(self):
        """Verifies that an authenticated user can retrieve an existing employee's details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        employee = Employee.objects.create(
            id_employee="EMP002",
            phone_number=3009876544,
            name="Laura",
            lastname="Martínez",
            document_id=1234567891,
            role="Supervisor",
            contract_date=date.today(),
            state="active"
        )
        response = self.client.get(reverse('employee-detail', args=[employee.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id_employee"], "EMP002")

    def test_authenticated_admin_can_update_employee(self):
        """Verifies that an authenticated user can update an existing employee"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        employee = Employee.objects.create(
            id_employee="EMP003",
            phone_number=3009876545,
            name="Carlos",
            lastname="Sánchez",
            document_id=1234567892,
            role="Worker",
            contract_date=date.today(),
            state="active"
        )

        updated_data = {
            "id_employee": "EMP003",
            "phone_number": 3009876545,
            "name": "Carlos",
            "lastname": "Ramírez",
            "document_id": 1234567892,
            "role": "Supervisor",
            "contract_date": str(date.today()),
            "state": "active"
        }

        response = self.client.put(reverse('employee-detail', args=[employee.id]), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["lastname"], "Ramírez")
        self.assertEqual(response.data["role"], "Supervisor")
