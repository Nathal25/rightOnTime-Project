from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator 

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

    # Puedes usar los campos 'first_name' y 'last_name' ya definidos en AbstractUser
    # Si quieres campos name y lastname separados puedes mapearlos o usar los originales

    # El email ya está en AbstractUser pero no es único por defecto, hacemos que sí:
    email = models.EmailField('Correo electrónico', unique=True)

    # El campo password ya es manejado por AbstractUser usando hashed passwords

    USERNAME_FIELD = 'username'  # Por defecto es 'username', se puede cambiar a 'email' si quieres
    REQUIRED_FIELDS = ['email', 'id_administrator', 'phone_number']

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
        ordering = ['id_administrator']

    def __str__(self):
        return f'{self.username} ({self.id_administrator})'
