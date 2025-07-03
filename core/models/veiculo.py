from django.db import models
from core.constants import LOCALIZACAO_CHOICES 

class Veiculo(models.Model):
    TIPO_CHOICES = [
        ('carro', 'Carro'),
        ('moto', 'Moto'),
        ('blindado', 'Blindado'),
        ('drone', 'Drone'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField(blank=True)
    modelo = models.CharField(max_length=100)
    ultima_manutencao = models.DateField()
    ativo = models.BooleanField(default=True)
    secret = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} {self.modelo}"

class EstoqueVeiculo(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='estoques')
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('veiculo', 'localizacao')

    def __str__(self):
        return f"{self.veiculo.tipo} - {self.veiculo.modelo} - {self.localizacao}: {self.quantidade}"