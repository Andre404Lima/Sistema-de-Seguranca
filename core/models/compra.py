from django.db import models
from core.constants import LOCALIZACAO_CHOICES 
from .user import CustomUser
ITEM_TIPO_CHOICES = (
    ('dispositivo', 'Dispositivo'),
    ('equipamento', 'Equipamento'),
    ('veiculo', 'Veículo'),
)

class SolicitacaoCompra(models.Model):
    criado_por = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tipo_item = models.CharField(max_length=20, choices=ITEM_TIPO_CHOICES)
    item_id = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField()
    destino = models.CharField(max_length=50, choices=LOCALIZACAO_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('autorizada', 'Autorizada'),
        ('negada', 'Negada'),
        ('convertida', 'Convertida em Ordem de Compra'),
    ], default='pendente') 

    def __str__(self):
        return f"{self.tipo_item} #{self.item_id} x{self.quantidade} - {self.status}"
    
    @property
    def nome_item(self):
        try:
            if self.tipo_item == 'dispositivo':
                from core.models import Dispositivo
                return Dispositivo.objects.get(id=self.item_id).nome
            elif self.tipo_item == 'equipamento':
                from core.models import Equipamento
                return Equipamento.objects.get(id=self.item_id).nome
            elif self.tipo_item == 'veiculo':
                from core.models import Veiculo
                return Veiculo.objects.get(id=self.item_id).modelo
        except:
            return 'Item não encontrado'


class OrdemCompra(models.Model):
    origem = models.ForeignKey(SolicitacaoCompra, on_delete=models.SET_NULL, null=True, blank=True)
    criado_por = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ordens_criadas')
    autorizado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordens_autorizadas')
    realizado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordens_pagas')

    tipo_item = models.CharField(max_length=20, choices=ITEM_TIPO_CHOICES)
    item_id = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField()
    destino = models.CharField(max_length=50, choices=LOCALIZACAO_CHOICES)

    status = models.CharField(max_length=20, choices=[
        ('autorizada', 'Autorizada'),
        ('paga', 'Paga'),
        ('negada', 'Negada'),
    ])
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_realizacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ordem #{self.id} - {self.tipo_item} #{self.item_id} x{self.quantidade} - {self.status}"
    
    def get_item_obj(self):
        from core.models import Dispositivo, Equipamento, Veiculo

        if self.tipo_item == 'dispositivo':
            return Dispositivo.objects.filter(id=self.item_id).first()
        elif self.tipo_item == 'equipamento':
            return Equipamento.objects.filter(id=self.item_id).first()
        elif self.tipo_item == 'veiculo':
            return Veiculo.objects.filter(id=self.item_id).first()
        return None

    def get_item_nome(self):
        obj = self.get_item_obj()
        if not obj:
            return str(self.item_id)
        
        if self.tipo_item == 'veiculo':
            return getattr(obj, 'modelo', str(self.item_id))
        else:
            return getattr(obj, 'nome', str(self.item_id))

    def __str__(self):
        nome = self.get_item_nome()
        return f"Ordem #{self.id} - {nome} x{self.quantidade} - {self.status}"


