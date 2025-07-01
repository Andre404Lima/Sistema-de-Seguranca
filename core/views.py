from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Equipamento, Dispositivo, Veiculo

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

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'core/dashboard.html', {'user': request.user})
#----------------------------------------------------------------------------
LOCALIZACOES_SECRETAS = [
    'BAT_CAVERNA',
    'POSTO_AVANCADO_CENTRO',
    'POSTO_AVANCADO_NORTE',
    'ESTACAO_SUBMERSA_PORTO'
]

@login_required
def lista_equipamentos(request):
    if request.user.user_type in ['batman', 'alfred']:
        equipamentos = Equipamento.objects.all()
    else:
        equipamentos = Equipamento.objects.filter(
            secret=False
        ).exclude(
            localizacao__in=LOCALIZACOES_SECRETAS
        )
    return render(request, 'core/lista_equipamentos.html', {'equipamentos': equipamentos})
#----------------------------------------------------------------------------
@login_required
def lista_dispositivos(request):
    if request.user.user_type in ['batman', 'alfred']:
        dispositivos = Dispositivo.objects.all()
    else:
        dispositivos = Dispositivo.objects.filter(
            secret=False
        ).exclude(
            localizacao__in=LOCALIZACOES_SECRETAS
        )
    return render(request, 'core/lista_equipamentos.html', {'equipamentos': dispositivos})
#----------------------------------------------------------------------------
@login_required
def lista_veiculos(request):
    if request.user.user_type in ['batman', 'alfred']:
        veiculos = Veiculo.objects.all()
    else:
        veiculos = Veiculo.objects.filter(
            secret=False
        ).exclude(
            localizacao__in=LOCALIZACOES_SECRETAS
        )
    return render(request, 'core/lista_equipamentos.html', {'equipamentos': veiculos})
