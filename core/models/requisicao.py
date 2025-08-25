from django.db import models
from django.contrib.auth import get_user_model
from core.models.dispositivo import Dispositivo
from core.models.equipamento import Equipamento
from core.models.veiculo import Veiculo

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

    @property
    def nome_item(self):
        if self.tipo_item == 'dispositivo':
            try:
                return Dispositivo.objects.get(id=self.item_id).nome
            except Dispositivo.DoesNotExist:
                return 'Dispositivo não encontrado'
        elif self.tipo_item == 'equipamento':
            try:
                return Equipamento.objects.get(id=self.item_id).nome
            except Equipamento.DoesNotExist:
                return 'Equipamento não encontrado'
        elif self.tipo_item == 'veiculo':
            try:
                return Veiculo.objects.get(id=self.item_id).modelo 
            except Veiculo.DoesNotExist:
                return 'Veículo não encontrado'
        return 'Tipo de item inválido'

    def __str__(self):
        return f"Movimentação de {self.quantidade} {self.nome_item} de {self.origem} para {self.destino}"
    
    
