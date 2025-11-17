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

    def test_checkout_without_checkin_returns_conflict(self):
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

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No hay check-in registrado hoy')

    def test_duplicate_checkout_not_possible_same_day(self):
        """Verify that an attendance record can only be checked out once"""
        # First check-out
        response1 = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify checkout_time was set
        self.attendance.refresh_from_db()
        first_checkout = self.attendance.check_out_time
        self.assertIsNotNone(first_checkout)
        
        # Attempt second check-out (should return conflict)
        response2 = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        # Should return 409 CONFLICT
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response2.data)

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

    def test_checkout_with_string_document_id(self):
        """Verify check-out works with string document ID"""
        response = self.client.post(
            self.url,
            {'document_id': str(self.employee.document_id)},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Salida registrada correctamente')

    def test_checkout_response_message_content(self):
        """Verify the exact message returned on successful check-out"""
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Salida registrada correctamente')

    def test_checkout_time_is_set_correctly(self):
        """Ensure check-out time is recorded and is reasonable"""
        before_checkout = datetime.now().time()
        
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.attendance.refresh_from_db()
        after_checkout = datetime.now().time()
        
        # Verify check-out time is between before and after
        self.assertIsNotNone(self.attendance.check_out_time)
        self.assertGreaterEqual(self.attendance.check_out_time, before_checkout)
        self.assertLessEqual(self.attendance.check_out_time, after_checkout)

    def test_multiple_employees_checkout_independently(self):
        """Verify multiple employees can check out independently"""
        # Create second employee with check-in
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

    def test_checkout_preserves_checkin_time(self):
        """Ensure check-out doesn't modify the original check-in time"""
        original_checkin_time = self.attendance.check_in_time

        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.attendance.refresh_from_db()
        self.assertEqual(self.attendance.check_in_time, original_checkin_time)

    def test_checkout_preserves_attendance_status(self):
        """Verify check-out doesn't change the attendance status"""
        original_status = self.attendance.status

        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.attendance.refresh_from_db()
        self.assertEqual(self.attendance.status, original_status)

    def test_checkout_inactive_employee(self):
        """Test check-out for an inactive employee with existing check-in"""
        # Create inactive employee with check-in
        inactive_employee = Employee.objects.create(
            id_employee='EMP203',
            phone_number=3445566778,
            name='Sofia',
            lastname='Garcia',
            document_id=4455667788,
            role='Operaria',
            contract_date=date.today(),
            state='inactive'
        )
        
        Attendance.objects.create(
            id_attendance='ATT-TEST-003',
            employee=inactive_employee,
            check_in_time=time(9, 0, 0),
            check_out_time=None,
            status='Present'
        )

        response = self.client.post(
            self.url,
            {'document_id': inactive_employee.document_id},
            format='json'
        )

        # Should still allow check-out
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_checkout_error_message_for_missing_checkin(self):
        """Verify specific error message when check-in doesn't exist"""
        employee_no_checkin = Employee.objects.create(
            id_employee='EMP204',
            phone_number=3556677889,
            name='Luis',
            lastname='Ramirez',
            document_id=5566778899,
            role='Supervisor',
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

    def test_checkout_error_message_for_nonexistent_employee(self):
        """Verify specific error message for non-existent employee"""
        response = self.client.post(
            self.url,
            {'document_id': 9988776655},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Empleado no existe')

    def test_checkout_error_message_for_missing_document_id(self):
        """Verify specific error message when document_id is missing"""
        response = self.client.post(
            self.url,
            {},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'document_id requerido')


class AttendanceListAllTestCase(APITestCase):
    """Test suite for listing all attendance records"""

    def setUp(self):
        """Create admin user and test data"""
        # Create an admin user for authentication
        test_password = 'test_secure_password_123'
        self.admin_user = Administrator.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password=test_password,
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

    def test_list_returns_attendance_data(self):
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

    def test_list_includes_all_created_records(self):
        """Verify all created attendance records are in the list"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Extract attendance IDs from response
        attendance_ids = [record['id_attendance'] for record in response.data]
        
        self.assertIn('ATT-LIST-001', attendance_ids)
        self.assertIn('ATT-LIST-002', attendance_ids)


class AttendanceCheckInTestCase(APITestCase):
    """Additional test cases for check-in functionality"""

    def setUp(self):
        """Setup test employee"""
        self.employee = Employee.objects.create(
            id_employee='EMP400',
            phone_number=3334445566,
            name='Roberto',
            lastname='Martinez',
            document_id=3333333333,
            role='Operario',
            contract_date=date.today(),
            state='active'
        )
        
        self.url = '/attendance/checkin/'

    def test_employee_can_check_in_successfully(self):
        """Verify employee can check in successfully"""
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_checkin_creates_attendance_record(self):
        """Verify check-in creates an attendance record"""
        initial_count = Attendance.objects.count()
        
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Attendance.objects.count(), initial_count + 1)

    def test_checkin_with_invalid_document_returns_404(self):
        """Verify check-in with invalid document returns 404"""
        response = self.client.post(
            self.url,
            {'document_id': 9999999999},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkin_without_document_id_returns_400(self):
        """Verify check-in without document_id returns 400"""
        response = self.client.post(
            self.url,
            {},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_checkin_returns_409(self):
        """Verify duplicate check-in on same day returns 409"""
        # First check-in
        self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        # Second check-in attempt
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_checkin_response_message(self):
        """Verify check-in returns correct success message"""
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Entrada registrada correctamente')

    def test_checkin_error_messages(self):
        """Verify specific error messages for different scenarios"""
        # Test missing document_id
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.data['error'], 'document_id requerido')
        
        # Test non-existent employee
        response = self.client.post(self.url, {'document_id': 9999999999}, format='json')
        self.assertEqual(response.data['error'], 'Empleado no existe')

    def test_checkin_sets_correct_time(self):
        """Verify check-in time is properly recorded"""
        before = datetime.now().time()
        
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        after = datetime.now().time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get the created attendance record
        attendance = Attendance.objects.filter(employee=self.employee).first()
        self.assertIsNotNone(attendance)
        self.assertGreaterEqual(attendance.check_in_time, before)
        self.assertLessEqual(attendance.check_in_time, after)

    def test_checkin_creates_unique_attendance_id(self):
        """Verify each check-in creates a unique attendance ID"""
        response = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify attendance was created with ID
        attendance = Attendance.objects.filter(employee=self.employee).first()
        self.assertIsNotNone(attendance)
        self.assertIsNotNone(attendance.id_attendance)
        self.assertTrue(attendance.id_attendance.startswith('A-'))

    def test_checkin_with_different_employees(self):
        """Verify multiple employees can check in on the same day"""
        employee2 = Employee.objects.create(
            id_employee='EMP401',
            phone_number=3445566778,
            name='Maria',
            lastname='Silva',
            document_id=4444444444,
            role='Operario',
            contract_date=date.today(),
            state='active'
        )
        
        # Both employees check in
        response1 = self.client.post(
            self.url,
            {'document_id': self.employee.document_id},
            format='json'
        )
        
        response2 = self.client.post(
            self.url,
            {'document_id': employee2.document_id},
            format='json'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify both have attendance records
        self.assertTrue(Attendance.objects.filter(employee=self.employee).exists())
        self.assertTrue(Attendance.objects.filter(employee=employee2).exists())
