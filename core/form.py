from django import forms
from django.db import models
from core.constants import LOCALIZACAO_CHOICES
from core.models.compra import ITEM_TIPO_CHOICES, SolicitacaoCompra, OrdemCompra
from core.models.dispositivo import Dispositivo
from core.models.equipamento import Equipamento
from core.models.manutencao import RequisicaoManutencao
from core.models.requisicao import RequisicaoMovimentacao
from core.models.veiculo import Veiculo  
from .models.user import CustomUser

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


class UserCreationFormCustom(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[])  # Será setado dinamicamente no __init__

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'user_type']

    def __init__(self, *args, user=None, tipos_permitidos=None, **kwargs):
        """
        user: usuário que está criando o novo usuário (opcional, para lógica extra futura)
        tipos_permitidos: lista com os tipos de usuários que podem ser selecionados no form
        """
        super().__init__(*args, **kwargs)

        choices_completas = [
            ('funcionario', 'Funcionário'),
            ('gerente', 'Gerente'),
            ('administrador', 'Administrador'),
            ('batman', 'Batman'),
            ('alfred', 'Alfred'),
        ]

        if tipos_permitidos is not None:
            self.fields['user_type'].choices = [t for t in choices_completas if t[0] in tipos_permitidos]
        else:
            self.fields['user_type'].choices = choices_completas

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user