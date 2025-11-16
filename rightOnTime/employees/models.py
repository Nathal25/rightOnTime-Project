from django.db import models
from django.core.validators import RegexValidator

class Employee(models.Model):
    id_employee = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name='ID Empleado'
    )

    phone_number = models.PositiveBigIntegerField(
        unique=False,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^(3|6)\d{9}$',
                message='No es un número de teléfono válido',
                code='invalid_phonenumber'
            )
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
            RegexValidator(
                regex=r'^\d{7,10}$',
                message='No es un número de documento válido',
                code='invalid_document_id'
            )
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

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['id_employee']

    def __str__(self):
        return f'{self.id_employee} - {self.name} {self.lastname}'
