import unicodedata
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models.manutencao import RequisicaoManutencao
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
    user = request.user

    requisicoes_manut = RequisicaoManutencao.objects.filter(
        status__in=['pendente', 'em_manutencao']
    )
    solicitacoes_compra = SolicitacaoCompra.objects.filter(status='pendente')
    ordens_compra = OrdemCompra.objects.filter(status='autorizada')

    requisicoes_pendentes = []

    for m in requisicoes_manut:
        requisicoes_pendentes.append({'tipo': 'manutencao', 'obj': m})

    if user.user_type == 'gerente':
        for s in solicitacoes_compra:
            requisicoes_pendentes.append({'tipo': 'compra', 'obj': s})

    if user.user_type in ['administrador', 'batman', 'alfred']:
        for o in ordens_compra:
            requisicoes_pendentes.append({'tipo': 'ordem', 'obj': o})

    # ordenar por data_criacao ou outro critério se quiser
    requisicoes_pendentes.sort(key=lambda x: getattr(x['obj'], 'data_criacao', None))

    locais_publicos = LOCALIZACAO_CHOICES[:7]
    locais_secretos = LOCALIZACAO_CHOICES[7:]

    locais_publicos_formatados = [{
        'valor': valor,
        'nome': nome,
        'imagem': formatar_nome_imagem(nome) + '.jpg'
    } for valor, nome in locais_publicos if valor]

    if user.user_type in ['batman', 'alfred']:
        locais_secretos_formatados = [{
            'valor': valor,
            'nome': nome,
            'imagem': formatar_nome_imagem(nome) + '.jpg'
        } for valor, nome in locais_secretos if valor]
    else:
        locais_secretos_formatados = []

    return render(request, 'core/dashboard.html', {
        'requisicoes_pendentes': requisicoes_pendentes,
        'user_type': user.user_type,
        'locais_publicos': locais_publicos_formatados,
        'locais_secretos': locais_secretos_formatados,
        # pode adicionar mais contextos aqui se precisar
    })
