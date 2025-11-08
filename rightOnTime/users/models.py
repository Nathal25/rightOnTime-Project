from django.db import models

# Create your models here.
from django.core.validators import RegexValidator 
from django.contrib.auth.models import AbstractUser, User 
class User(AbstractUser): 
    phone_number = models.PositiveBigIntegerField( 
    unique=False,blank=False,null=False, 
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
        verbose_name = 'Usuario' 
        verbose_name_plural = 'Usuarios' 
        ordering = ['id'] 