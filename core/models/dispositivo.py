from django.db import models
from core.constants import LOCALIZACAO_CHOICES
from django.utils import timezone

class Dispositivo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ultima_manutencao = models.DateField()
    ativo = models.BooleanField(default=True)
    secret = models.BooleanField(default=False)
    imagem = models.ImageField(upload_to='dispositivos', null=True, blank=True)

    def __str__(self):
        return self.nome


class EstoqueDispositivo(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='estoques')
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('dispositivo', 'localizacao')

    def __str__(self):
        return f"{self.dispositivo.nome} - {self.localizacao}: {self.quantidade}"


