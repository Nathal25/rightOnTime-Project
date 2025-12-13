from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Employee(models.Model):
    id_employee = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name='ID Empleado'
    )

    phone_number = models.PositiveBigIntegerField(
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinValueValidator(3000000000, message='El teléfono debe empezar con 3 o 6 y tener 10 dígitos'),
            MaxValueValidator(6999999999, message='El teléfono debe empezar con 3 o 6 y tener 10 dígitos')
        ],
        verbose_name='Número teléfono'
    )

    name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Nombre'
    )

    lastname = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Apellido'
    )

    document_id = models.PositiveBigIntegerField(
        unique=True,
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1000000, message='El documento debe tener entre 7 y 10 dígitos'),
            MaxValueValidator(9999999999, message='El documento debe tener entre 7 y 10 dígitos')
        ],
        verbose_name='Cédula ciudadanía'
    )

    role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='Employee',
        verbose_name='Rol'
    )

    contract_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de contrato'
    )

    state = models.CharField(
        max_length=20,
        choices=(('active', 'Activo'), ('inactive', 'Inactivo')),
        default='active',
        verbose_name='Estado'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de creación'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['id_employee']

    def __str__(self):
        return f'{self.id_employee} - {self.name} {self.lastname}'
