import unicodedata
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models.manutencao import RequisicaoManutencao
from core.models.requisicao import RequisicaoMovimentacao
from core.models import Dispositivo, Equipamento, Veiculo, AcaoUsuario
from core.models.compra import SolicitacaoCompra, OrdemCompra
from core.constants import LOCALIZACAO_CHOICES
from core.form import UserCreationFormCustom

def formatar_nome_imagem(nome):
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    return ''.join(c for c in nome_sem_acento if c.isalnum())

@login_required
def dashboard(request):
    user = request.user

    requisicoes_manut = RequisicaoManutencao.objects.filter(
        status__in=['pendente', 'em_manutencao', 'autorizada']
    )
    solicitacoes_compra = SolicitacaoCompra.objects.filter(status='pendente')
    ordens_compra = OrdemCompra.objects.filter(status='autorizada')
    requisicoes_movimentacao = RequisicaoMovimentacao.objects.filter(status='pendente')

    requisicoes_pendentes = []

    for m in requisicoes_manut:
        requisicoes_pendentes.append({'tipo': 'manutencao', 'obj': m})

    for mov in requisicoes_movimentacao:
        requisicoes_pendentes.append({'tipo': 'movimentacao', 'obj': mov})

    if user.user_type in ['gerente', 'funcionario']:
        for s in solicitacoes_compra:
            requisicoes_pendentes.append({'tipo': 'compra', 'obj': s})

    if user.user_type in ['gerente', 'administrador', 'batman', 'alfred']:
        for o in ordens_compra:
            requisicoes_pendentes.append({'tipo': 'ordem', 'obj': o})

    requisicoes_pendentes.sort(key=lambda x: getattr(x['obj'], 'data_criacao', None) or '')


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

    if user.user_type == 'funcionario':
        acoes = AcaoUsuario.objects.filter(usuario__user_type='funcionario')
        pode_criar = False
        tipos_permitidos = []
    elif user.user_type == 'gerente':
        acoes = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente'])
        pode_criar = False
        tipos_permitidos = []
    elif user.user_type == 'administrador':
        acoes = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente', 'administrador'])
        pode_criar = True
        tipos_permitidos = ['funcionario', 'gerente', 'administrador']
    elif user.user_type in ['batman', 'alfred']:
        acoes = AcaoUsuario.objects.all()
        pode_criar = (user.user_type == 'batman')
        tipos_permitidos = ['funcionario', 'gerente', 'administrador', 'batman', 'alfred']
    else:
        acoes = AcaoUsuario.objects.none()
        pode_criar = False
        tipos_permitidos = []

    acoes = acoes.order_by('-data_hora')[:50]
    acoes_formatadas = [{
        'usuario_nome': acao.usuario.username,
        'usuario_tipo': acao.usuario.user_type,
        'acao': acao.acao,
        'data_hora': acao.data_hora,
    } for acao in acoes]

    form = None
    if pode_criar:
        if request.method == 'POST':
            form = UserCreationFormCustom(request.POST, tipos_permitidos=tipos_permitidos)
            if form.is_valid():
                form.save()
                return redirect('dashboard')
        else:
            form = UserCreationFormCustom(tipos_permitidos=tipos_permitidos)

    return render(request, 'core/dashboard.html', {
        'requisicoes_pendentes': requisicoes_pendentes,
        'user_type': user.user_type,
        'locais_publicos': locais_publicos_formatados,
        'locais_secretos': locais_secretos_formatados,
        'acoes_usuarios': acoes_formatadas,
        'pode_criar_user': pode_criar,
        'form': form,
    })
