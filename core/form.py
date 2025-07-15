from django import forms
from core.constants import LOCALIZACAO_CHOICES
from core.models.compra import ITEM_TIPO_CHOICES, SolicitacaoCompra, OrdemCompra
from core.models.requisicao import RequisicaoMovimentacao  

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
