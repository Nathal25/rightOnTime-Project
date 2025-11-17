"""
Pruebas de integración para el flujo de check-in de asistencia
Código de estudiante: 2024076
"""
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date
from attendance.models import Attendance
from employees.models import Employee


class StudentCheckInTest(APITestCase):
    """Prueba de integración para el endpoint de check-in"""

    def setUp(self):
        """Prepara un empleado para las pruebas"""
        self.employee = Employee.objects.create(
            id_employee='EMP2024',
            phone_number=3001234567,
            name='Estudiante',
            lastname='Prueba',
            document_id=2024076000,
            role='Tester',
            contract_date=date.today(),
            state='active'
        )
        self.url = '/attendance/checkin/'

    def test_check_in_creates_attendance_record(self):
        """Verifica que un check-in válido cree un registro de asistencia"""
        response = self.client.post(
            self.url,
            {'document_id': 2024076000},
            format='json'
        )
        # Debe devolver 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe contener un mensaje de éxito
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Entrada registrada correctamente')
        # Debe haber creado un registro en la base de datos
        self.assertTrue(Attendance.objects.filter(employee=self.employee).exists())

    def test_check_in_with_invalid_document_fails(self):
        """Verifica que un documento inexistente devuelva error 404"""
        response = self.client.post(
            self.url,
            {'document_id': 9999999999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)