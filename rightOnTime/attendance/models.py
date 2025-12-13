from django.db import models
from django.utils import timezone
from employees.models import Employee

# Create your models here.
class Attendance(models.Model):
    id_attendance = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name='ID Asistencia'
    )

    date = models.DateField(
        auto_now_add=True,
        blank=False,
        null=False,
        verbose_name='Fecha'
    )

    check_in_time = models.TimeField(
        blank=False,
        null=False,
        verbose_name='Hora de entrada'
    )

    check_out_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Hora de salida'
    )

    status = models.CharField(
        default='Present',
        max_length=20,
        blank=False,
        null=False,
        verbose_name='Estado'
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Empleado'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de creación'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    def __str__(self):
        return f'Asistencia {self.id_attendance} - Empleado {self.employee.id_employee}'
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'