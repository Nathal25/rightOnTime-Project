from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from .models import Attendance
from employees.models import Employee
from .serializers import AttendanceSerializer


class AttendanceSerializerTest(TestCase):
    """Test cases for AttendanceSerializer"""
    
    def setUp(self):
        from datetime import date
        self.employee = Employee.objects.create(
            id_employee="EMP001",
            document_id=1001,
            name="John",
            lastname="Doe",
            phone_number=3001234567,
            contract_date=date.today()
        )
        self.attendance = Attendance.objects.create(
            id_attendance="A-001",
            employee=self.employee,
            check_in_time=timezone.now().time()
        )
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid attendance data"""
        serializer = AttendanceSerializer(instance=self.attendance)
        self.assertIn('id_attendance', serializer.data)
        self.assertIn('employee', serializer.data)
        self.assertIn('check_in_time', serializer.data)


class CheckInViewTest(APITestCase):
    """Test cases for check_in view"""
    
    def setUp(self):
        from datetime import date
        self.client = APIClient()
        self.url = '/attendance/check-in/'
        self.employee = Employee.objects.create(
            id_employee="EMP002",
            document_id=1234,
            name="Jane",
            lastname="Smith",
            phone_number=3001234568,
            contract_date=date.today()
        )
    
    def test_check_in_success(self):
        """Test successful check-in"""
        data = {'document_id': '1234'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertTrue(Attendance.objects.filter(employee=self.employee).exists())
    
    def test_check_in_missing_document_id(self):
        """Test check-in without document_id"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_check_in_employee_not_found(self):
        """Test check-in with non-existent employee"""
        data = {'document_id': '9999'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_check_in_duplicate(self):
        """Test duplicate check-in on same day"""
        # First check-in
        data = {'document_id': '1234'}
        self.client.post(self.url, data, format='json')
        
        # Second check-in (should fail)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)


class CheckOutViewTest(APITestCase):
    """Test cases for check_out view"""
    
    def setUp(self):
        from datetime import date
        self.client = APIClient()
        self.url = '/attendance/check-out/'
        self.employee = Employee.objects.create(
            id_employee="EMP003",
            document_id=5678,
            name="Bob",
            lastname="Johnson",
            phone_number=3001234569,
            contract_date=date.today()
        )
    
    def test_check_out_success(self):
        """Test successful check-out"""
        # Create a check-in first
        Attendance.objects.create(
            id_attendance="A-test",
            employee=self.employee,
            check_in_time=timezone.now().time()
        )
        
        data = {'document_id': '5678'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify check_out_time was set
        attendance = Attendance.objects.get(employee=self.employee)
        self.assertIsNotNone(attendance.check_out_time)
    
    def test_check_out_missing_document_id(self):
        """Test check-out without document_id"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_check_out_employee_not_found(self):
        """Test check-out with non-existent employee"""
        data = {'document_id': '9999'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_check_out_no_check_in(self):
        """Test check-out without prior check-in"""
        data = {'document_id': '5678'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)


class ListAllAttendanceViewTest(APITestCase):
    """Test cases for list_all_attendance view"""
    
    def setUp(self):
        from datetime import date
        from employees.models import Employee as EmployeeUser
        self.client = APIClient()
        self.url = '/attendance/list/'
        self.employee = Employee.objects.create(
            id_employee="EMP004",
            document_id=1111,
            name="Alice",
            lastname="Williams",
            phone_number=3001234570,
            contract_date=date.today()
        )
        # Create a staff user for authentication
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username="alice",
            document_id=1111,
            password="testpass123"
        )
        user.is_staff = True
        user.save()
        self.client.force_authenticate(user=user)
    
    def test_list_attendance_authenticated(self):
        """Test listing attendance with authentication"""
        # Create some attendance records
        Attendance.objects.create(
            id_attendance="A-001",
            employee=self.employee,
            check_in_time=timezone.now().time()
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
