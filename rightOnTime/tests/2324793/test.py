from datetime import date, datetime

from rest_framework import status
from rest_framework.test import APITestCase

from attendance.models import Attendance
from employees.models import Employee


class AttendanceCheckInTestCase(APITestCase):
	"""Test suite for attendance check-in endpoint"""

	def setUp(self):
		"""Create an employee to be used across the tests"""
		self.employee = Employee.objects.create(
			id_employee='EMP100',
			phone_number=3001112233,
			name='Maria',
			lastname='Gonzalez',
			document_id=9876543210,
			role='Operaria',
			contract_date=date.today(),
			state='active'
		)
		self.url = '/attendance/checkin/'
		print("Setup complete: Employee created with ID", self.employee)

	def test_employee_check_in_creates_attendance_record(self):
		"""Ensure the endpoint registers attendance for a valid document"""
		response = self.client.post(
			self.url,
			{'document_id': self.employee.document_id},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('message', response.data)

		attendance_exists = Attendance.objects.filter(employee=self.employee).exists()
		self.assertTrue(attendance_exists)
		print("Response Data:", response.data)

	def test_duplicate_check_in_same_day_returns_conflict(self):
		"""Verify the endpoint blocks multiple check-ins on the same day"""
		Attendance.objects.create(
			id_attendance='ATT-001',
			employee=self.employee,
			check_in_time=datetime.now().time()
		)

		response = self.client.post(
			self.url,
			{'document_id': self.employee.document_id},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertIn('error', response.data)
		print("Response Data:", response.data)
