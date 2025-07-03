from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Equipamento, Dispositivo, Veiculo
from .models.dispositivo import EstoqueDispositivo
from .models.equipamento import EstoqueEquipamento
from .models.veiculo import EstoqueVeiculo
from django.db.models import Prefetch
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
    else:
        # usuário comum só vê dispositivos públicos
        equipamentos = base_qs.filter(secret=False)

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    equipamentos_com_dados = []

    for equip in equipamentos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = equip.estoques.all()
        else:
            # filtra os estoques com base nos locais secretos
            estoques_visiveis = [
                est for est in equip.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,                 # False→público, True→secreto
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()  # alfabética
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
        'localizacoes_secretas': LOCALIZACOES_SECRETAS,
    })
# ------------------- DISPOSITIVOS -------------------------------------------
@login_required
def lista_dispositivos(request):
    base_qs = Dispositivo.objects.prefetch_related('estoques').order_by('secret', 'nome')  

    if request.user.user_type in ['batman', 'alfred']:
        dispositivos = base_qs
    else:
        # usuário comum só vê dispositivos públicos
        dispositivos = base_qs.filter(secret=False)

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    dispositivos_com_dados = []

    for disp in dispositivos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = disp.estoques.all()
        else:
            # filtra os estoques com base nos locais secretos
            estoques_visiveis = [
                est for est in disp.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,                 # False→público, True→secreto
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()  # alfabética
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
        'localizacoes_secretas': LOCALIZACOES_SECRETAS,
    })
# ------------------- VEÍCULOS ----------------------------------------------------
@login_required
def lista_veiculos(request):
    base_qs = Veiculo.objects.prefetch_related('estoques').order_by('secret', 'modelo')  

    if request.user.user_type in ['batman', 'alfred']:
        veiculos = base_qs
    else:
        # usuário comum só vê dispositivos públicos
        veiculos = base_qs.filter(secret=False)

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    veiculos_com_dados = []

    for veic in veiculos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = veic.estoques.all()
        else:
            # filtra os estoques com base nos locais secretos
            estoques_visiveis = [
                est for est in veic.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,                 # False→público, True→secreto
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()  # alfabética
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
        'localizacoes_secretas': LOCALIZACOES_SECRETAS,
    })
#-------------------------LOCAIS DASBOARD---------------------------------------------------
@login_required
def dashboard_view(request):
    user = request.user
    tipo = user.user_type

    locais_publicos = LOCALIZACAO_CHOICES[:7]
    locais_secretos = LOCALIZACAO_CHOICES[7:]

    # Mostrar tudo para batman ou alfred
    if tipo in ['batman', 'alfred']:
        localizacoes = locais_publicos + locais_secretos
    else:
        localizacoes = locais_publicos

    return render(request, 'core/dashboard.html', {
    'locais_publicos': locais_publicos,
    'locais_secretos': locais_secretos,
    'user_type': tipo,
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
            )
            equipamentos_estoque = (
                EstoqueEquipamento.objects
                .filter(localizacao=local)
                .select_related('equipamento')
            )
            veiculos_estoque = (
                EstoqueVeiculo.objects
                .filter(localizacao=local)
                .select_related('veiculo')
            )
        else:
            dispositivos_estoque = (
                EstoqueDispositivo.objects
                .filter(localizacao=local, dispositivo__secret=False)
                .select_related('dispositivo')
            )
            equipamentos_estoque = (
                EstoqueEquipamento.objects
                .filter(localizacao=local, equipamento__secret=False)
                .select_related('equipamento')
            )
            veiculos_estoque = (
                EstoqueVeiculo.objects
                .filter(localizacao=local, veiculo__secret=False)
                .select_related('veiculo')
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