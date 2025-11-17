from datetime import date, datetime, time
from rest_framework import status
from rest_framework.test import APITestCase
from attendance.models import Attendance
from employees.models import Employee


class AttendanceCheckOutTestCase(APITestCase):
    """Test suite for attendance check-out endpoint"""

    def setUp(self):
        """Create an employee and existing attendance record for testing"""
        # Create a test employee
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
            check_in_time=time(8, 0, 0),  # 8:00 AM
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
        
        # Verify the attendance record was updated with check-out time
        self.attendance.refresh_from_db()
        self.assertIsNotNone(self.attendance.check_out_time)

    def test_checkout_without_checkin_returns_not_found(self):
        """Ensure check-out fails if no check-in exists for the day"""
        # Create another employee without check-in
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

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_duplicate_checkout_returns_conflict(self):
        """Verify that checking out twice on the same day returns conflict"""
        # First check-out
        self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        # Attempt second check-out
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)

    def test_checkout_with_invalid_document_returns_not_found(self):
        """Ensure check-out with non-existent document ID returns 404"""
        response = self.client.post(
            self.url,
            {'document_id': 9999999999},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_checkout_without_document_id_returns_bad_request(self):
        """Verify that missing document_id returns 400 Bad Request"""
        response = self.client.post(
            self.url,
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_checkout_updates_attendance_record_correctly(self):
        """Confirm that check-out properly updates the attendance record"""
        initial_checkout_time = self.attendance.check_out_time
        self.assertIsNone(initial_checkout_time)

        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh and verify the record was updated
        self.attendance.refresh_from_db()
        self.assertIsNotNone(self.attendance.check_out_time)
        self.assertEqual(self.attendance.status, 'Present')
