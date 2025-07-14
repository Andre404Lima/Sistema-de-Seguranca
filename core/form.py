from django import forms
from .models import RequisicaoMovimentacao

class RequisicaoMovimentacaoForm(forms.ModelForm):
    class Meta:
        model = RequisicaoMovimentacao
        fields = ['tipo_item', 'item_id', 'origem', 'destino', 'quantidade']