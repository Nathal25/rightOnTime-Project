"""
Tests completos para aumentar la cobertura del proyecto RightOnTime
Incluye tests de modelos, serializers, vistas API, validaciones y casos edge
"""
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, date, time
from attendance.models import Attendance
from employees.models import Employee
from attendance.serializers import AttendanceSerializer
from employees.serializers import EmployeeSerializer
from administrator.models import Administrator


# ========================
# 1. TESTS DE MODELOS
# ========================

class EmployeeModelTest(TestCase):
    """Tests para el modelo Employee"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.employee_data = {
            'id_employee': 'EMP001',
            'phone_number': 3001234567,
            'name': 'Juan',
            'lastname': 'Pérez',
            'document_id': 1234567890,
            'role': 'Developer',
            'contract_date': date(2024, 1, 15),
            'state': 'active'
        }
    
    def test_create_employee_success(self):
        """Test: Crear un empleado exitosamente"""
        employee = Employee.objects.create(**self.employee_data)
        self.assertEqual(employee.id_employee, 'EMP001')
        self.assertEqual(employee.name, 'Juan')
        self.assertEqual(employee.state, 'active')
        self.assertIsNotNone(employee.created_at)
    
    def test_employee_str_representation(self):
        """Test: Representación en string del empleado"""
        employee = Employee.objects.create(**self.employee_data)
        expected_str = f'EMP001 - Juan Pérez'
        self.assertEqual(str(employee), expected_str)
    
    def test_employee_unique_id(self):
        """Test: El ID de empleado debe ser único"""
        Employee.objects.create(**self.employee_data)
        with self.assertRaises(Exception):  # IntegrityError
            Employee.objects.create(**self.employee_data)
    
    def test_employee_unique_document_id(self):
        """Test: El número de documento debe ser único"""
        Employee.objects.create(**self.employee_data)
        duplicate_data = self.employee_data.copy()
        duplicate_data['id_employee'] = 'EMP002'
        with self.assertRaises(Exception):  # IntegrityError
            Employee.objects.create(**duplicate_data)
    
    def test_employee_inactive_state(self):
        """Test: Empleado con estado inactivo"""
        self.employee_data['state'] = 'inactive'
        employee = Employee.objects.create(**self.employee_data)
        self.assertEqual(employee.state, 'inactive')
    
    def test_employee_ordering(self):
        """Test: Los empleados se ordenan por id_employee"""
        Employee.objects.create(id_employee='EMP003', name='Carlos', lastname='Gómez',
                               document_id=9876543210, phone_number=3109876543,
                               role='Manager', contract_date=date(2024, 2, 1))
        Employee.objects.create(id_employee='EMP001', name='Ana', lastname='López',
                               document_id=1122334455, phone_number=3201122334,
                               role='Designer', contract_date=date(2024, 1, 1))
        employees = Employee.objects.all()
        self.assertEqual(employees[0].id_employee, 'EMP001')
        self.assertEqual(employees[1].id_employee, 'EMP003')


class AttendanceModelTest(TestCase):
    """Tests para el modelo Attendance"""
    
    def setUp(self):
        """Configuración inicial"""
        self.employee = Employee.objects.create(
            id_employee='EMP001',
            phone_number=3001234567,
            name='María',
            lastname='García',
            document_id=1234567890,
            role='Developer',
            contract_date=date(2024, 1, 15)
        )
    
    def test_create_attendance_success(self):
        """Test: Crear asistencia exitosamente"""
        attendance = Attendance.objects.create(
            id_attendance='A-001',
            employee=self.employee,
            check_in_time=time(9, 0, 0),
            status='Present'
        )
        self.assertEqual(attendance.status, 'Present')
        self.assertIsNotNone(attendance.date)
        self.assertEqual(attendance.employee, self.employee)
    
    def test_attendance_str_representation(self):
        """Test: Representación en string de asistencia"""
        attendance = Attendance.objects.create(
            id_attendance='A-001',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        expected_str = f'Asistencia A-001 - Empleado EMP001'
        self.assertEqual(str(attendance), expected_str)
    
    def test_attendance_with_checkout(self):
        """Test: Asistencia con hora de salida"""
        attendance = Attendance.objects.create(
            id_attendance='A-002',
            employee=self.employee,
            check_in_time=time(9, 0, 0),
            check_out_time=time(18, 0, 0)
        )
        self.assertIsNotNone(attendance.check_out_time)
        self.assertEqual(attendance.check_out_time, time(18, 0, 0))
    
    def test_attendance_without_checkout(self):
        """Test: Asistencia sin hora de salida (null permitido)"""
        attendance = Attendance.objects.create(
            id_attendance='A-003',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        self.assertIsNone(attendance.check_out_time)
    
    def test_attendance_default_status(self):
        """Test: Estado por defecto es 'Present'"""
        attendance = Attendance.objects.create(
            id_attendance='A-004',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        self.assertEqual(attendance.status, 'Present')
    
    def test_attendance_cascade_delete(self):
        """Test: Eliminar empleado elimina sus asistencias (CASCADE)"""
        Attendance.objects.create(
            id_attendance='A-005',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        employee_id = self.employee.id
        self.employee.delete()
        # Verificar que las asistencias también se eliminaron
        attendances = Attendance.objects.filter(employee_id=employee_id)
        self.assertEqual(attendances.count(), 0)
    
    def test_attendance_unique_id(self):
        """Test: El ID de asistencia debe ser único"""
        Attendance.objects.create(
            id_attendance='A-UNIQUE',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        with self.assertRaises(Exception):  # IntegrityError
            Attendance.objects.create(
                id_attendance='A-UNIQUE',
                employee=self.employee,
                check_in_time=time(10, 0, 0)
            )


# ========================
# 2. TESTS DE SERIALIZERS
# ========================

class EmployeeSerializerTest(TestCase):
    """Tests para EmployeeSerializer"""
    
    def setUp(self):
        self.employee_data = {
            'id_employee': 'EMP100',
            'phone_number': 3001234567,
            'name': 'Pedro',
            'lastname': 'Martínez',
            'document_id': 9988776655,
            'role': 'Tester',
            'contract_date': '2024-03-01',
            'state': 'active'
        }
    
    def test_serializer_with_valid_data(self):
        """Test: Serializer con datos válidos"""
        serializer = EmployeeSerializer(data=self.employee_data)
        self.assertTrue(serializer.is_valid())
        employee = serializer.save()
        self.assertEqual(employee.name, 'Pedro')
        self.assertEqual(employee.id_employee, 'EMP100')
    
    def test_serializer_with_missing_required_fields(self):
        """Test: Serializer con campos requeridos faltantes"""
        incomplete_data = {'name': 'Pedro'}
        serializer = EmployeeSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('id_employee', serializer.errors)
    
    def test_serializer_read_operation(self):
        """Test: Serializar un empleado existente"""
        employee = Employee.objects.create(**{
            'id_employee': 'EMP101',
            'phone_number': 3109876543,
            'name': 'Laura',
            'lastname': 'Rodríguez',
            'document_id': 1122334455,
            'role': 'Manager',
            'contract_date': date(2024, 2, 1)
        })
        serializer = EmployeeSerializer(employee)
        self.assertEqual(serializer.data['name'], 'Laura')
        self.assertEqual(serializer.data['id_employee'], 'EMP101')


class AttendanceSerializerTest(TestCase):
    """Tests para AttendanceSerializer"""
    
    def setUp(self):
        self.employee = Employee.objects.create(
            id_employee='EMP200',
            phone_number=3001234567,
            name='Sofia',
            lastname='González',
            document_id=5566778899,
            role='Developer',
            contract_date=date(2024, 1, 10)
        )
    
    def test_serializer_with_valid_data(self):
        """Test: Serializer con datos válidos"""
        attendance_data = {
            'id_attendance': 'A-100',
            'employee': self.employee.id,
            'check_in_time': '09:00:00',
            'status': 'Present'
        }
        serializer = AttendanceSerializer(data=attendance_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        attendance = serializer.save()
        self.assertEqual(attendance.id_attendance, 'A-100')
    
    def test_serializer_with_checkout_time(self):
        """Test: Serializer con hora de salida"""
        attendance_data = {
            'id_attendance': 'A-101',
            'employee': self.employee.id,
            'check_in_time': '09:00:00',
            'check_out_time': '18:00:00',
            'status': 'Present'
        }
        serializer = AttendanceSerializer(data=attendance_data)
        self.assertTrue(serializer.is_valid())
        attendance = serializer.save()
        self.assertIsNotNone(attendance.check_out_time)
    
    def test_serializer_read_operation(self):
        """Test: Serializar asistencia existente"""
        attendance = Attendance.objects.create(
            id_attendance='A-102',
            employee=self.employee,
            check_in_time=time(9, 30, 0)
        )
        serializer = AttendanceSerializer(attendance)
        self.assertEqual(serializer.data['id_attendance'], 'A-102')
        self.assertEqual(serializer.data['status'], 'Present')


# ========================
# 3. TESTS DE VISTAS/API
# ========================

class CheckInAPITest(APITestCase):
    """Tests para la vista check_in"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/attendance/checkin/'
        self.employee = Employee.objects.create(
            id_employee='EMP300',
            phone_number=3001234567,
            name='Carlos',
            lastname='Hernández',
            document_id=1234567890,
            role='Developer',
            contract_date=date(2024, 1, 5)
        )
    
    def test_check_in_success(self):
        """Test: Check-in exitoso"""
        data = {'document_id': 1234567890}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Entrada registrada correctamente')
        # Verificar que se creó la asistencia
        self.assertTrue(Attendance.objects.filter(employee=self.employee).exists())
    
    def test_check_in_without_document_id(self):
        """Test: Check-in sin document_id"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'document_id requerido')
    
    def test_check_in_employee_not_found(self):
        """Test: Check-in con empleado inexistente"""
        data = {'document_id': 9999999999}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Empleado no existe')
    
    def test_check_in_duplicate_same_day(self):
        """Test: Check-in duplicado el mismo día"""
        # Primer check-in
        Attendance.objects.create(
            id_attendance='A-TEST',
            employee=self.employee,
            check_in_time=time(8, 0, 0)
        )
        # Intentar segundo check-in
        data = {'document_id': 1234567890}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Este empleado ya tiene asistencia hoy')


class CheckOutAPITest(APITestCase):
    """Tests para la vista check_out"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/attendance/checkout/'
        self.employee = Employee.objects.create(
            id_employee='EMP400',
            phone_number=3109876543,
            name='Ana',
            lastname='Ramírez',
            document_id=9876543210,
            role='Designer',
            contract_date=date(2024, 2, 10)
        )
    
    def test_check_out_success(self):
        """Test: Check-out exitoso"""
        # Crear check-in previo
        attendance = Attendance.objects.create(
            id_attendance='A-CHECKOUT-TEST',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        data = {'document_id': 9876543210}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Salida registrada correctamente')
        # Verificar que se actualizó el check_out_time
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.check_out_time)
    
    def test_check_out_without_document_id(self):
        """Test: Check-out sin document_id"""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_check_out_employee_not_found(self):
        """Test: Check-out con empleado inexistente"""
        data = {'document_id': 1111111111}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_check_out_without_check_in(self):
        """Test: Check-out sin check-in previo"""
        data = {'document_id': 9876543210}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No hay check-in registrado hoy')


class ListAllAttendanceAPITest(APITestCase):
    """Tests para la vista list_all_attendance"""
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/attendance/all/'
        # Crear usuario para autenticación (si es necesario)
        self.user = Administrator.objects.create_user(
            username='testuser', 
            password='testpass123',
            email='testuser@example.com',
            id_administrator='ADM001',
            phone_number=3001234567
        )
        
        # Crear empleados y asistencias
        self.employee1 = Employee.objects.create(
            id_employee='EMP500',
            phone_number=3001234567,
            name='Luis',
            lastname='Torres',
            document_id=1111222233,
            role='Developer',
            contract_date=date(2024, 1, 1)
        )
        self.employee2 = Employee.objects.create(
            id_employee='EMP501',
            phone_number=3109876543,
            name='Elena',
            lastname='Vargas',
            document_id=4444555566,
            role='Tester',
            contract_date=date(2024, 1, 15)
        )
        Attendance.objects.create(
            id_attendance='A-500',
            employee=self.employee1,
            check_in_time=time(9, 0, 0)
        )
        Attendance.objects.create(
            id_attendance='A-501',
            employee=self.employee2,
            check_in_time=time(9, 15, 0)
        )
    
    def test_list_attendance_with_authentication(self):
        """Test: Listar asistencias con autenticación"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_list_attendance_without_authentication(self):
        """Test: Listar asistencias sin autenticación debe fallar"""
        response = self.client.get(self.url)
        # Esperamos un 401 o 403 dependiendo de la configuración
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


# ========================
# 4. TESTS DE VIEWSETS
# ========================

class EmployeeViewSetTest(APITestCase):
    """Tests para EmployeeViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        # Crear usuario para autenticación
        self.user = Administrator.objects.create_user(
            username='admin', 
            password='admin123',
            email='admin@example.com',
            id_administrator='ADM002',
            phone_number=3109876543
        )
        self.client.force_authenticate(user=self.user)
        
        self.employee_data = {
            'id_employee': 'EMP600',
            'phone_number': 3001234567,
            'name': 'Roberto',
            'lastname': 'Sánchez',
            'document_id': 7788990011,
            'role': 'Manager',
            'contract_date': '2024-01-20',
            'state': 'active'
        }
    
    def test_create_employee_via_api(self):
        """Test: Crear empleado vía API"""
        response = self.client.post('/employees/', self.employee_data, format='json')
        # Puede ser 201 o 200 dependiendo de configuración
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_list_employees_via_api(self):
        """Test: Listar empleados vía API"""
        Employee.objects.create(**{
            'id_employee': 'EMP601',
            'phone_number': 3109876543,
            'name': 'Diana',
            'lastname': 'Cruz',
            'document_id': 2233445566,
            'role': 'Developer',
            'contract_date': date(2024, 2, 1)
        })
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ========================
# 5. TESTS DE VALIDACIÓN
# ========================

class EmployeeValidationTest(TestCase):
    """Tests de validación de datos del modelo Employee"""
    
    def test_invalid_phone_number(self):
        """Test: Número de teléfono inválido"""
        # Teléfono que no empieza con 3 o 6
        with self.assertRaises(ValidationError):
            employee = Employee(
                id_employee='EMP700',
                phone_number=2001234567,  # Inválido
                name='Test',
                lastname='User',
                document_id=1234567890,
                role='Developer',
                contract_date=date(2024, 1, 1)
            )
            employee.full_clean()
    
    def test_invalid_document_id_too_short(self):
        """Test: Documento muy corto"""
        with self.assertRaises(ValidationError):
            employee = Employee(
                id_employee='EMP701',
                phone_number=3001234567,
                name='Test',
                lastname='User',
                document_id=123456,  # Solo 6 dígitos, mínimo 7
                role='Developer',
                contract_date=date(2024, 1, 1)
            )
            employee.full_clean()


# ========================
# 6. TESTS DE CASOS EDGE
# ========================

class EdgeCaseTest(TestCase):
    """Tests de casos límite y especiales"""
    
    def setUp(self):
        self.employee = Employee.objects.create(
            id_employee='EMP800',
            phone_number=3001234567,
            name='Edge',
            lastname='Case',
            document_id=1234567890,
            role='Tester',
            contract_date=date(2024, 1, 1)
        )
    
    def test_multiple_attendances_different_days(self):
        """Test: Múltiples asistencias en días diferentes"""
        attendance1 = Attendance.objects.create(
            id_attendance='A-800',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        # Simular día diferente (manualmente)
        attendance2 = Attendance.objects.create(
            id_attendance='A-801',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        # Cambiar fecha manualmente
        attendance2.date = date(2024, 1, 2)
        attendance2.save()
        
        attendances = Attendance.objects.filter(employee=self.employee)
        self.assertEqual(attendances.count(), 2)
    
    def test_employee_with_very_long_name(self):
        """Test: Empleado con nombre muy largo (límite 150 caracteres)"""
        long_name = 'A' * 150
        employee = Employee.objects.create(
            id_employee='EMP801',
            phone_number=3109876543,
            name=long_name,
            lastname='Test',
            document_id=9988776655,
            role='Developer',
            contract_date=date(2024, 1, 1)
        )
        self.assertEqual(len(employee.name), 150)
    
    def test_attendance_related_name(self):
        """Test: Uso de related_name 'attendances' desde Employee"""
        Attendance.objects.create(
            id_attendance='A-802',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        Attendance.objects.create(
            id_attendance='A-803',
            employee=self.employee,
            check_in_time=time(9, 0, 0)
        )
        # Usar related_name
        attendances = self.employee.attendances.all()
        self.assertEqual(attendances.count(), 2)


# ========================
# 7. TESTS DE INTEGRACIÓN
# ========================

class IntegrationTest(APITestCase):
    """Tests de integración completos"""
    
    def test_full_attendance_workflow(self):
        """Test: Flujo completo de asistencia (crear empleado -> check-in -> check-out)"""
        # 1. Crear empleado
        employee = Employee.objects.create(
            id_employee='EMP900',
            phone_number=3001234567,
            name='Workflow',
            lastname='Test',
            document_id=1122334455,
            role='Developer',
            contract_date=date(2024, 1, 1)
        )
        
        # 2. Check-in
        response = self.client.post('/attendance/checkin/', 
                                   {'document_id': 1122334455}, 
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Verificar asistencia creada
        attendance = Attendance.objects.filter(employee=employee).first()
        self.assertIsNotNone(attendance)
        self.assertIsNone(attendance.check_out_time)
        
        # 4. Check-out
        response = self.client.post('/attendance/checkout/', 
                                   {'document_id': 1122334455}, 
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Verificar check-out actualizado
        attendance.refresh_from_db()
        self.assertIsNotNone(attendance.check_out_time)
