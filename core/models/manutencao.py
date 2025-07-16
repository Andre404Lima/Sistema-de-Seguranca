from core import models
from core.constants import LOCALIZACAO_CHOICES
from core.models.user import CustomUser
from django.db import models




class RequisicaoManutencao(models.Model):
    TIPO_CHOICES = (
        ('dispositivo', 'Dispositivo'),
        ('equipamento', 'Equipamento'),
        ('veiculo', 'Veículo'),
    )
    
    tipo_item = models.CharField(max_length=20, choices=TIPO_CHOICES)
    item_id = models.PositiveIntegerField()
    localizacao = models.CharField(max_length=50, choices=LOCALIZACAO_CHOICES)
    quantidade = models.PositiveIntegerField()
    criado_por = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),          
        ('aprovada', 'Aprovada'),          
        ('negada', 'Negada'),
        ('em_manutencao', 'Em Manutenção'),
        ('concluida', 'Concluída'),
    ], default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    def get_item_obj(self):
        from core.models import Dispositivo, Equipamento, Veiculo
        if self.tipo_item == 'dispositivo':
            return Dispositivo.objects.filter(id=self.item_id).first()
        elif self.tipo_item == 'equipamento':
            return Equipamento.objects.filter(id=self.item_id).first()
        elif self.tipo_item == 'veiculo':
            return Veiculo.objects.filter(id=self.item_id).first()
        
    def get_item_nome(self):
        obj = self.get_item_obj()
        if obj:
            if self.tipo_item == 'veiculo':
                return getattr(obj, 'modelo', f"ID {self.item_id}")
            return getattr(obj, 'nome', f"ID {self.item_id}")
        return f"Item #{self.item_id}"

