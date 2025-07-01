from django.db import models
from core.constants import LOCALIZACAO_CHOICES 

class Equipamento(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    quantidade = models.PositiveIntegerField(default=1)
    ultima_manutencao = models.DateField()
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    secret = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} (x{self.quantidade}) - {self.get_localizacao_display()}"
