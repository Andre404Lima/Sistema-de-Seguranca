from django.db import models
from core.constants import LOCALIZACAO_CHOICES 

class Veiculo(models.Model):
    TIPO_CHOICES = [
        ('carro', 'Carro'),
        ('moto', 'Moto'),
        ('blindado', 'Blindado'),
        ('dronado', 'Drone'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True)
    modelo = models.CharField(max_length=100)
    placa = models.CharField(max_length=20, unique=True)
    quantidade = models.PositiveIntegerField(default=1)
    ultima_manutencao = models.DateField()
    ativo = models.BooleanField(default=True)
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    secret = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.modelo} ({self.placa}) - {self.get_localizacao_display()}"
