from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator 

class Employee(AbstractUser):
    # Añadir related_name para evitar conflictos con Administrator
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='employee_set',
        related_query_name='employee',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='employee_set',
        related_query_name='employee',
    )
    
    phone_number = models.PositiveBigIntegerField( 
        unique=False, blank=False, null=False, 
        validators=[ 
            RegexValidator(
                regex=r'^(3|6)\d{9}$',
                message=('No es un número de teléfono válido'), 
                code='invalid_phonenumber' 
                ) 
                ], 
                verbose_name='Número teléfono' 
                ) 
    id_employee = models.CharField(
        default=None,
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name='ID Empleado'
)


    name = models.CharField(
        default=None,
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Nombre'
)


    lastname = models.CharField(
        default=None,
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Apellido'
)


    document_id = models.PositiveBigIntegerField(
        default=None,
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^\d{7,10}$',
                message=('No es un número de documento válido'),
                code='invalid_document_id'
                )
                ],
                verbose_name='Cédula ciudadania'
                )


role = models.CharField(
    default=None,
    max_length=50,
    blank=False,
    null=False,
    verbose_name='Rol'
)


contract_date = models.DateField(
    default=None,
    blank=False,
    null=False,
    verbose_name='Fecha de contrato'
)


state = models.CharField(
    max_length=20,
    choices=(('active', 'Activo'), ('inactive', 'Inactivo')),
    default='active',
    verbose_name='Estado'
    )


USERNAME_FIELD = 'username'
REQUIRED_FIELDS = ['id_employee', 'name', 'lastname', 'document_id', 'role', 'contract_date', 'state']


class Meta: 
   verbose_name = 'Empleado' 
   verbose_name_plural = 'Empleados' 
   ordering = ['id']

