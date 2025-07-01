from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('funcionario', 'Funcionário'),
        ('gerente', 'Gerente'),
        ('administrador', 'Administrador'),
        ('batman', 'Batman'),
        ('alfred','Alfred')
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='funcionario')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
