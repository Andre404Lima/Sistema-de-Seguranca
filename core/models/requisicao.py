from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RequisicaoMovimentacao(models.Model):
    ITEM_TIPO_CHOICES = (
        ('dispositivo', 'Dispositivo'),
        ('equipamento', 'Equipamento'),
        ('veiculo', 'Veículo'),
    )
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('autorizada', 'Autorizada'),
        ('rejeitada', 'Rejeitada'),
    ]

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pendente')
    tipo_item = models.CharField(max_length=20, choices=ITEM_TIPO_CHOICES)
    item_id = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField()
    origem = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)

    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisicoes_solicitadas')
    autorizado = models.BooleanField(default=False)
    autorizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisicoes_autorizadas')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movimentação de {self.quantidade} {self.tipo_item} de {self.origem} para {self.destino}"