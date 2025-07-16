from django import forms
from django.db import models
from core.constants import LOCALIZACAO_CHOICES
from core.models.compra import ITEM_TIPO_CHOICES, SolicitacaoCompra, OrdemCompra
from core.models.dispositivo import Dispositivo
from core.models.equipamento import Equipamento
from core.models.manutencao import RequisicaoManutencao
from core.models.requisicao import RequisicaoMovimentacao
from core.models.veiculo import Veiculo  

class RequisicaoMovimentacaoForm(forms.ModelForm):
    class Meta:
        model = RequisicaoMovimentacao
        fields = ['tipo_item', 'item_id', 'origem', 'destino', 'quantidade']

class SolicitacaoCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoCompra
        fields = ['tipo_item', 'item_id', 'quantidade', 'destino']
        widgets = {
            'tipo_item': forms.Select(choices=ITEM_TIPO_CHOICES),
            'quantidade': forms.NumberInput(attrs={'min': 1}),
            'destino': forms.Select(choices=LOCALIZACAO_CHOICES),
        }

class OrdemCompraForm(forms.ModelForm):
    class Meta:
        model = OrdemCompra
        fields = ['tipo_item', 'item_id', 'quantidade', 'destino']
        widgets = {
            'tipo_item': forms.Select(choices=ITEM_TIPO_CHOICES),
            'quantidade': forms.NumberInput(attrs={'min': 1}),
            'destino': forms.Select(choices=LOCALIZACAO_CHOICES),
        }

class RequisicaoManutencaoForm(forms.ModelForm):
    class Meta:
        model = RequisicaoManutencao
        fields = ['tipo_item', 'item_id', 'localizacao', 'quantidade']
        widgets = {
            'tipo_item': forms.Select(choices=RequisicaoManutencao.TIPO_CHOICES),
            'localizacao': forms.Select(choices=LOCALIZACAO_CHOICES),
            'quantidade': forms.NumberInput(attrs={'min': 1}),
        }

class DispositivoForm(forms.ModelForm):
    ultima_manutencao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),label='Última Manutenção')
    secret = models.BooleanField(default=False)

    class Meta:
        model = Dispositivo
        fields = ['nome', 'descricao', 'ultima_manutencao', 'ativo', 'secret', 'imagem']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or user.user_type not in ['batman', 'alfred']:
            self.fields.pop('secret')


class EquipamentoForm(forms.ModelForm):
    ultima_manutencao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),label='Última Manutenção')
    secret = models.BooleanField(default=False)

    class Meta:
        model = Equipamento
        fields = ['nome', 'descricao', 'ultima_manutencao', 'secret', 'imagem']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or user.user_type not in ['batman', 'alfred']:
            self.fields.pop('secret')


class VeiculoForm(forms.ModelForm):
    ultima_manutencao = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),label='Última Manutenção')
    secret = models.BooleanField(default=False)

    class Meta:
        model = Veiculo
        fields = ['tipo', 'modelo', 'descricao', 'ultima_manutencao', 'ativo', 'secret', 'imagem']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is None or user.user_type not in ['batman', 'alfred']:
            self.fields.pop('secret')
