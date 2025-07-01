from django.db import models
from core.constants import LOCALIZACAO_CHOICES  # ✅ necessário

class Dispositivo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=1)
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    ativo = models.BooleanField(default=True)
    ultima_manutencao = models.DateField()
    secret = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} - {self.get_localizacao_display()}"

