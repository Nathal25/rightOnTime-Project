from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator 

class Administrator(AbstractUser):
    # Añadir related_name para evitar conflictos con Employee
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='administrator_set',
        related_query_name='administrator',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='administrator_set',
        related_query_name='administrator',
    )
    
    id_administrator = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        verbose_name='ID Administrador'
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

    # Puedes usar los campos 'first_name' y 'last_name' ya definidos en AbstractUser
    # Si quieres campos name y lastname separados puedes mapearlos o usar los originales

    # El email ya está en AbstractUser pero no es único por defecto, hacemos que sí:
    email = models.EmailField('Correo electrónico', unique=True)

    # El campo password ya es manejado por AbstractUser usando hashed passwords

    USERNAME_FIELD = 'username'  # Por defecto es 'username', se puede cambiar a 'email' si quieres
    REQUIRED_FIELDS = ['email', 'id_administrator', 'phone_number']

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de creación'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
        ordering = ['id_administrator']

    def __str__(self):
        return f'{self.username} ({self.id_administrator})'
