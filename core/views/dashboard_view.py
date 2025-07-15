import unicodedata
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models.requisicao import RequisicaoMovimentacao
from core.models import Dispositivo, Equipamento, Veiculo
from core.constants import LOCALIZACAO_CHOICES
from core.models.compra import SolicitacaoCompra, OrdemCompra

def formatar_nome_imagem(nome):
    # Remove acentos e caracteres especiais, preserva maiúsculas/minúsculas
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    return ''.join(c for c in nome_sem_acento if c.isalnum())

@login_required
def dashboard(request):
    tipo = request.user.user_type
    locais_publicos = LOCALIZACAO_CHOICES[:7]
    locais_secretos = LOCALIZACAO_CHOICES[7:]
    requisicoes_pendentes = []
    solicitacoes_pendentes = []
    ordens_pendentes_pagamento = []

    locais_publicos_formatados = [{
        'valor': valor,
        'nome': nome,
        'imagem': formatar_nome_imagem(nome) + '.jpg'
    } for valor, nome in locais_publicos if valor]

    if tipo in ['batman', 'alfred']:
        locais_secretos_formatados = [{
            'valor': valor,
            'nome': nome,
            'imagem': formatar_nome_imagem(nome) + '.jpg'
        } for valor, nome in locais_secretos if valor]
    else:
        locais_secretos_formatados = []

    if tipo in ['gerente', 'batman', 'alfred']:
        requisicoes_pendentes = RequisicaoMovimentacao.objects.filter(status='pendente')
        for req in requisicoes_pendentes:
            obj = None
            if req.tipo_item == 'dispositivo':
                obj = Dispositivo.objects.filter(id=req.item_id).first()
            elif req.tipo_item == 'equipamento':
                obj = Equipamento.objects.filter(id=req.item_id).first()
            elif req.tipo_item == 'veiculo':
                obj = Veiculo.objects.filter(id=req.item_id).first()
            req.item_nome = getattr(obj, 'nome', None) or getattr(obj, 'modelo', None) or "Item desconhecido"

    if tipo == 'gerente':
        solicitacoes_pendentes = SolicitacaoCompra.objects.filter(status='pendente')

    if tipo in ['administrador', 'batman']:
        ordens_pendentes_pagamento = OrdemCompra.objects.filter(status='autorizada')

    return render(request, 'core/dashboard.html', {
        'locais_publicos': locais_publicos_formatados,
        'locais_secretos': locais_secretos_formatados,
        'user_type': tipo,
        'requisicoes': requisicoes_pendentes,
        'solicitacoes': solicitacoes_pendentes,
        'ordens': ordens_pendentes_pagamento,
    })