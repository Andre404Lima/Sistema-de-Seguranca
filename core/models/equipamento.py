from django.db import models
from core.constants import LOCALIZACAO_CHOICES 

class Equipamento(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ultima_manutencao = models.DateField()
    secret = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome}"

class EstoqueEquipamento(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='estoques')
    localizacao = models.CharField(max_length=30, choices=LOCALIZACAO_CHOICES)
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('equipamento', 'localizacao')

    def __str__(self):
        return f"{self.equipamento.nome} - {self.localizacao}: {self.quantidade}"