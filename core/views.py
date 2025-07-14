from datetime import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models.requisicao import RequisicaoMovimentacao
from .models import Equipamento, Dispositivo, Veiculo
from .models.dispositivo import EstoqueDispositivo
from .models.equipamento import EstoqueEquipamento
from .models.veiculo import EstoqueVeiculo
from .form import RequisicaoMovimentacaoForm
from .models.requisicao import RequisicaoMovimentacao
from .constants import LOCALIZACAO_CHOICES


#----------------------------LOGIN------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # redirecionar para dashboard após login
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'core/login.html')
#--------------------------LOGOUT--------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'core/dashboard.html', {'user': request.user})
#---------------------------LOCAIS SECRETOS-----------------------------------------------
LOCALIZACOES_SECRETAS = [
    'BAT_CAVERNA',
    'POSTO_AVANCADO_CENTRO',
    'POSTO_AVANCADO_NORTE',
    'ESTACAO_SUBMERSA_PORTO'
]
# ------------------- EQUIPAMENTOS -------------------------------------------
@login_required
def lista_equipamentos(request):
    base_qs = Equipamento.objects.prefetch_related('estoques').order_by('secret', 'nome')

    if request.user.user_type in ['batman', 'alfred']:
        equipamentos = base_qs
        locais_visiveis = LOCALIZACAO_CHOICES
    else:
        equipamentos = base_qs.filter(secret=False)
        locais_visiveis = [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS]

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    equipamentos_com_dados = []

    for equip in equipamentos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = equip.estoques.all()
        else:
            estoques_visiveis = [
                est for est in equip.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        # Filtrar estoques com quantidade > 0
        estoques_visiveis = [est for est in estoques_visiveis if est.quantidade > 0]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            )
        )

        total = sum(est.quantidade for est in estoques_visiveis)

        equipamentos_com_dados.append({
            'obj': equip,
            'estoques': estoques_visiveis,
            'total': total,
        })

    return render(request, 'core/lista_equipamentos.html', {
        'equipamentos': equipamentos_com_dados,
        'localizacoes_visiveis': locais_visiveis,
    })


# ------------------- DISPOSITIVOS -------------------------------------------
@login_required
def lista_dispositivos(request):
    base_qs = Dispositivo.objects.order_by('secret', 'nome')

    if request.user.user_type in ['batman', 'alfred']:
        dispositivos = base_qs
        locais_visiveis = LOCALIZACAO_CHOICES
    else:
        dispositivos = base_qs.filter(secret=False)
        locais_visiveis = [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS]

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    dispositivos_com_dados = []

    for disp in dispositivos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = list(EstoqueDispositivo.objects.filter(dispositivo=disp))
        else:
            estoques_visiveis = list(
                EstoqueDispositivo.objects.filter(dispositivo=disp).exclude(localizacao__in=LOCALIZACOES_SECRETAS)
            )

        # Filtrar estoques com quantidade > 0
        estoques_visiveis = [est for est in estoques_visiveis if est.quantidade > 0]

        estoques_visiveis.sort(
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            )
        )

        total = sum(est.quantidade for est in estoques_visiveis)

        dispositivos_com_dados.append({
            'obj': disp,
            'estoques': estoques_visiveis,
            'total': total,
        })

    return render(request, 'core/lista_dispositivos.html', {
        'dispositivos': dispositivos_com_dados,
        'localizacoes_visiveis': locais_visiveis,
    })


# ------------------- VEÍCULOS ----------------------------------------------------
@login_required
def lista_veiculos(request):
    base_qs = Veiculo.objects.prefetch_related('estoques').order_by('secret', 'modelo')

    if request.user.user_type in ['batman', 'alfred']:
        veiculos = base_qs
        locais_visiveis = LOCALIZACAO_CHOICES
    else:
        veiculos = base_qs.filter(secret=False)
        locais_visiveis = [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS]

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    veiculos_com_dados = []

    for veic in veiculos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = veic.estoques.all()
        else:
            estoques_visiveis = [
                est for est in veic.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        # Filtrar estoques com quantidade > 0
        estoques_visiveis = [est for est in estoques_visiveis if est.quantidade > 0]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            )
        )

        total = sum(est.quantidade for est in estoques_visiveis)

        veiculos_com_dados.append({
            'obj': veic,
            'estoques': estoques_visiveis,
            'total': total,
        })

    return render(request, 'core/lista_veiculos.html', {
        'veiculos': veiculos_com_dados,
        'localizacoes_visiveis': locais_visiveis,
    })
#-------------------------DASBOARD-------------------------------------------------------------
@login_required
def dashboard_view(request):
    tipo = request.user.user_type

    locais_publicos = LOCALIZACAO_CHOICES[:7]
    locais_secretos = LOCALIZACAO_CHOICES[7:]

    # Carrega requisições pendentes apenas para cargos autorizados
    requisicoes_pendentes = []
    if tipo in ['gerente', 'batman', 'alfred']:
        requisicoes_pendentes = RequisicaoMovimentacao.objects.filter(status='pendente')

    return render(request, 'core/dashboard.html', {
        'locais_publicos': locais_publicos,
        'locais_secretos': locais_secretos if tipo in ['batman', 'alfred'] else [],
        'user_type': tipo,
        'requisicoes': requisicoes_pendentes,
    })

#-------------------------ITENS POR LOCAL---------------------------------------------------
@login_required
def itens_por_local(request, local):
    locais_secretos = [cod for cod, nome in LOCALIZACAO_CHOICES[7:]]
    nome_local = dict(LOCALIZACAO_CHOICES).get(local, local)
    user_type = request.user.user_type
    acesso_restrito = local in locais_secretos and user_type not in ['batman', 'alfred']

    if acesso_restrito:
        dispositivos_estoque = []
        equipamentos_estoque = []
        veiculos_estoque     = []
    else:
        if user_type in ['batman', 'alfred']:
            dispositivos_estoque = (
                EstoqueDispositivo.objects
                .filter(localizacao=local)
                .select_related('dispositivo')
                .order_by('dispositivo__secret', 'dispositivo__nome')
            )
            equipamentos_estoque = (
                EstoqueEquipamento.objects
                .filter(localizacao=local)
                .select_related('equipamento')
                .order_by('equipamento__secret', 'equipamento__nome')
            )
            veiculos_estoque = (
                EstoqueVeiculo.objects
                .filter(localizacao=local)
                .select_related('veiculo')
                .order_by('veiculo__secret', 'veiculo__modelo')
            )
        else:
            dispositivos_estoque = (
                EstoqueDispositivo.objects
                .filter(localizacao=local, dispositivo__secret=False)
                .select_related('dispositivo')
                .order_by('dispositivo__nome')
            )
            equipamentos_estoque = (
                EstoqueEquipamento.objects
                .filter(localizacao=local, equipamento__secret=False)
                .select_related('equipamento')
                .order_by('equipamento__nome')
            )
            veiculos_estoque = (
                EstoqueVeiculo.objects
                .filter(localizacao=local, veiculo__secret=False)
                .select_related('veiculo')
                .order_by('veiculo__tipo', 'veiculo__modelo')
            )
    return render(
        request,
        'core/itens_por_local.html',
        {
            'local': nome_local,
            'dispositivos_estoque': dispositivos_estoque,
            'equipamentos_estoque': equipamentos_estoque,
            'veiculos_estoque': veiculos_estoque,
        },
    )
#-------------------------RequisicaoMovimentacao---------------------------------------------------
@login_required
def solicitar_movimentacao(request):
    if request.method == 'POST':
        form = RequisicaoMovimentacaoForm(request.POST)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.solicitante = request.user

            tipo = requisicao.tipo_item
            item_id = requisicao.item_id
            qtd = requisicao.quantidade
            origem = requisicao.origem
            destino = requisicao.destino

            # Define modelo de estoque e filtro conforme tipo
            if tipo == 'dispositivo':
                estoque_model = EstoqueDispositivo
                filtro = {'dispositivo_id': item_id}
            elif tipo == 'equipamento':
                estoque_model = EstoqueEquipamento
                filtro = {'equipamento_id': item_id}
            elif tipo == 'veiculo':
                estoque_model = EstoqueVeiculo
                filtro = {'veiculo_id': item_id}
            else:
                messages.error(request, "Tipo inválido.")
                return redirect('dashboard')

            # Usuários autorizados movem diretamente
            if request.user.user_type in ['gerente', 'batman', 'alfred']:
                requisicao.status = 'autorizada'
                requisicao.autorizado = True
                requisicao.autorizador = request.user
                requisicao.save()

                origem_estoque = estoque_model.objects.filter(localizacao=origem, **filtro).first()
                if not origem_estoque or origem_estoque.quantidade < qtd:
                    messages.error(request, "Estoque insuficiente na origem.")
                    return redirect('dashboard')

                origem_estoque.quantidade -= qtd
                origem_estoque.save()

                destino_estoque, created = estoque_model.objects.get_or_create(localizacao=destino, **filtro)
                destino_estoque.quantidade += qtd
                destino_estoque.save()

                messages.success(request, "Movimentação realizada com sucesso.")

            else:
                # Usuários comuns criam requisição pendente
                requisicao.status = 'pendente'
                requisicao.save()
                messages.success(request, "Requisição enviada para aprovação.")

            return redirect('dashboard')

        else:
            messages.error(request, "Formulário inválido. Verifique os dados.")
            print(form.errors)
    return redirect('dashboard')
#-------------------------autorizarMovimentacao---------------------------------------------------
@login_required
def autorizar_requisicao(request, req_id):
    user = request.user
    if user.user_type not in ['gerente', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para autorizar.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoMovimentacao, pk=req_id)

    if requisicao.status != 'pendente':
        messages.warning(request, "Requisição já foi processada.")
        return redirect('dashboard')

    tipo = requisicao.tipo_item  # corrigido aqui
    item_id = requisicao.item_id
    qtd = requisicao.quantidade
    origem = requisicao.origem  # corrigido aqui
    destino = requisicao.destino  # corrigido aqui

    if tipo == 'dispositivo':
        estoque_model = EstoqueDispositivo
        filtro = {'dispositivo_id': item_id}
    elif tipo == 'equipamento':
        estoque_model = EstoqueEquipamento
        filtro = {'equipamento_id': item_id}
    elif tipo == 'veiculo':
        estoque_model = EstoqueVeiculo
        filtro = {'veiculo_id': item_id}
    else:
        messages.error(request, "Tipo inválido.")
        return redirect('dashboard')

    origem_estoque = estoque_model.objects.filter(localizacao=origem, **filtro).first()
    if not origem_estoque or origem_estoque.quantidade < qtd:
        messages.error(request, "Estoque insuficiente na origem.")
        return redirect('dashboard')

    origem_estoque.quantidade -= qtd
    origem_estoque.save()

    destino_estoque, _ = estoque_model.objects.get_or_create(localizacao=destino, **filtro)
    destino_estoque.quantidade += qtd
    destino_estoque.save()

    requisicao.status = 'autorizada'
    requisicao.autorizador = user  # corrigido aqui (no seu código estava 'autorizado_por')
    requisicao.save()

    messages.success(request, "Requisição autorizada com sucesso.")
    return redirect('dashboard')
#-------------------------negarMovimentacao---------------------------------------------------
@login_required
def rejeitar_requisicao(request, pk):
    if request.user.user_type not in ['gerente', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoMovimentacao, pk=pk)
    if requisicao.status == 'pendente':
        requisicao.status = 'rejeitada'
        requisicao.autorizador = request.user  # corrigido aqui
        requisicao.save()
        messages.info(request, "Requisição rejeitada.")
    
    return redirect('dashboard')