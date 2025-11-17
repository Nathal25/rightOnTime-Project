from datetime import date, datetime, time

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from attendance.models import Attendance
from employees.models import Employee
from administrator.models import Administrator


class AttendanceCheckOutTestCase(APITestCase):
	"""Test suite for attendance check-out endpoint"""

	def setUp(self):
		"""Create an employee and existing attendance record for testing"""
		self.employee = Employee.objects.create(
			id_employee='EMP200',
			phone_number=3112223344,
			name='Carlos',
			lastname='Rodriguez',
			document_id=1122334455,
			role='Supervisor',
			contract_date=date.today(),
			state='active'
		)
		
		# Create an existing check-in attendance record
		self.attendance = Attendance.objects.create(
			id_attendance='ATT-TEST-001',
			employee=self.employee,
			check_in_time=time(8, 0, 0),
			check_out_time=None,
			status='Present'
		)
		
		self.url = '/attendance/checkout/'

	def test_employee_can_check_out_successfully(self):
		"""Verify that an employee can successfully check out"""
		response = self.client.post(
			self.url,
			{'document_id': self.employee.document_id},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('message', response.data)
		self.assertEqual(response.data['message'], 'Salida registrada correctamente')
		
		# Verify the attendance record was updated with check-out time
		self.attendance.refresh_from_db()
		self.assertIsNotNone(self.attendance.check_out_time)

	def test_checkout_without_checkin_returns_conflict(self):
		"""Ensure check-out fails if no check-in exists for the day"""
		employee_no_checkin = Employee.objects.create(
			id_employee='EMP201',
			phone_number=3223334455,
			name='Ana',
			lastname='Martinez',
			document_id=2233445566,
			role='Operaria',
			contract_date=date.today(),
			state='active'
		)

		response = self.client.post(
			self.url,
			{'document_id': employee_no_checkin.document_id},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertIn('error', response.data)
		self.assertEqual(response.data['error'], 'No hay check-in registrado hoy')

	def test_checkout_with_invalid_document_returns_404(self):
		"""Ensure check-out with non-existent document ID returns 404"""
		response = self.client.post(
			self.url,
			{'document_id': 9999999999},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertIn('error', response.data)
		self.assertEqual(response.data['error'], 'Empleado no existe')

	def test_checkout_without_document_id_returns_400(self):
		"""Verify that missing document_id returns 400 Bad Request"""
		response = self.client.post(
			self.url,
			{},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('error', response.data)
		self.assertEqual(response.data['error'], 'document_id requerido')

	def test_checkout_updates_only_checkout_time(self):
		"""Confirm that check-out only updates checkout time, not other fields"""
		original_checkin_time = self.attendance.check_in_time
		original_status = self.attendance.status

		response = self.client.post(
			self.url,
			{'document_id': self.employee.document_id},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		self.attendance.refresh_from_db()
		self.assertEqual(self.attendance.check_in_time, original_checkin_time)
		self.assertEqual(self.attendance.status, original_status)
		self.assertIsNotNone(self.attendance.check_out_time)

	def test_checkout_multiple_employees_same_day(self):
		"""Verify multiple employees can check out independently on the same day"""
		employee2 = Employee.objects.create(
			id_employee='EMP202',
			phone_number=3334445566,
			name='Pedro',
			lastname='Lopez',
			document_id=3344556677,
			role='Operario',
			contract_date=date.today(),
			state='active'
		)
		
		attendance2 = Attendance.objects.create(
			id_attendance='ATT-TEST-002',
			employee=employee2,
			check_in_time=time(8, 30, 0),
			check_out_time=None,
			status='Present'
		)

		# First employee checks out
		response1 = self.client.post(
			self.url,
			{'document_id': self.employee.document_id},
			format='json'
		)

		# Second employee checks out
		response2 = self.client.post(
			self.url,
			{'document_id': employee2.document_id},
			format='json'
		)

		self.assertEqual(response1.status_code, status.HTTP_200_OK)
		self.assertEqual(response2.status_code, status.HTTP_200_OK)

		# Verify both have check-out times
		self.attendance.refresh_from_db()
		attendance2.refresh_from_db()
		self.assertIsNotNone(self.attendance.check_out_time)
		self.assertIsNotNone(attendance2.check_out_time)


class AttendanceListAllTestCase(APITestCase):
	"""Test suite for listing all attendance records"""

	def setUp(self):
		"""Create admin user and test data"""
		self.admin_user = Administrator.objects.create_user(
			username='admin_test',
			email='admin@test.com',
			password='test_secure_password_123',
			id_administrator='ADM001',
			phone_number=3001234567,
			is_staff=True
		)
		
		# Generate JWT token
		refresh = RefreshToken.for_user(self.admin_user)
		self.access_token = str(refresh.access_token)
		
		# Create test employees
		self.employee1 = Employee.objects.create(
			id_employee='EMP300',
			phone_number=3112223344,
			name='Ana',
			lastname='Perez',
			document_id=1111111111,
			role='Operario',
			contract_date=date.today(),
			state='active'
		)
		
		self.employee2 = Employee.objects.create(
			id_employee='EMP301',
			phone_number=3223334455,
			name='Mario',
			lastname='Lopez',
			document_id=2222222222,
			role='Supervisor',
			contract_date=date.today(),
			state='active'
		)
		
		# Create attendance records
		self.attendance1 = Attendance.objects.create(
			id_attendance='ATT-LIST-001',
			employee=self.employee1,
			check_in_time=time(8, 0, 0),
			check_out_time=time(17, 0, 0),
			status='Present'
		)
		
		self.attendance2 = Attendance.objects.create(
			id_attendance='ATT-LIST-002',
			employee=self.employee2,
			check_in_time=time(8, 30, 0),
			check_out_time=None,
			status='Present'
		)
		
		self.url = '/attendance/list/'

	def test_authenticated_admin_can_list_all_attendance(self):
		"""Verify that authenticated admin can list all attendance records"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.url)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIsInstance(response.data, list)
		self.assertGreaterEqual(len(response.data), 2)

	def test_unauthenticated_user_cannot_list_attendance(self):
		"""Verify that unauthenticated user cannot access the list"""
		response = self.client.get(self.url)
		
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_list_returns_correct_attendance_data(self):
		"""Verify that list returns proper attendance data structure"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.url)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		# Check that response contains expected fields
		if len(response.data) > 0:
			first_record = response.data[0]
			self.assertIn('id_attendance', first_record)
			self.assertIn('employee_id', first_record)
			self.assertIn('check_in_time', first_record)
			self.assertIn('date', first_record)

	def test_list_includes_all_created_records(self):
		"""Verify all created attendance records are in the list"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.url)
		
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		
		# Extract attendance IDs from response
		attendance_ids = [record['id_attendance'] for record in response.data]
		
		self.assertIn('ATT-LIST-001', attendance_ids)
		self.assertIn('ATT-LIST-002', attendance_ids)
