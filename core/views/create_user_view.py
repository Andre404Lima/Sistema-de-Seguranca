from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from core.form import UserCreationFormCustom
from core.models.acao_user import AcaoUsuario
from core.models.user import CustomUser

@login_required
def controle_usuarios(request):
    user_type = request.user.user_type

    if user_type == 'funcionario':
        base_qs = AcaoUsuario.objects.filter(usuario__user_type='funcionario').order_by('-data_hora')
        pode_criar = False
        tipos_permitidos = []
        usuarios = CustomUser.objects.none()

    elif user_type == 'gerente':
        base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente']).order_by('-data_hora')
        pode_criar = False
        tipos_permitidos = []
        usuarios = CustomUser.objects.filter(user_type__in=['funcionario', 'gerente'], is_active=True)

    elif user_type == 'administrador':
        base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente', 'administrador']).order_by('-data_hora')
        pode_criar = True
        tipos_permitidos = ['funcionario', 'gerente', 'administrador']
        usuarios = CustomUser.objects.filter(user_type__in=['funcionario', 'gerente', 'administrador'], is_active=True)

    elif user_type in ['batman', 'alfred']:
        base_qs = AcaoUsuario.objects.all().order_by('-data_hora')
        pode_criar = (user_type == 'batman')
        tipos_permitidos = ['funcionario', 'gerente', 'administrador', 'batman', 'alfred']
        usuarios = CustomUser.objects.filter(is_active=True)

    else:
        base_qs = AcaoUsuario.objects.none()
        pode_criar = False
        tipos_permitidos = []
        usuarios = CustomUser.objects.none()

    acoes_recentes = base_qs[:50]  

    acoes_por_cargo = defaultdict(list)
    for acao in acoes_recentes:
        acoes_por_cargo[acao.usuario.user_type].append({
            'usuario_nome': acao.usuario.username,
            'acao': acao.acao,
            'data_hora': acao.data_hora,
        })

    if request.method == 'POST' and pode_criar:
        form = UserCreationFormCustom(request.POST, tipos_permitidos=tipos_permitidos)
        if form.is_valid():
            novo_usuario = form.save()
            AcaoUsuario.objects.create(
                usuario=request.user,
                acao=f"Usuário '{novo_usuario.username}' criado com tipo '{novo_usuario.user_type}'"
            )
            return redirect('controle_usuarios')
    else:
        form = UserCreationFormCustom(tipos_permitidos=tipos_permitidos)

    return render(request, 'core/controle_usuarios.html', {
        'usuarios': usuarios,
        'pode_criar': pode_criar,
        'form': form,
        'acoes_por_cargo': dict(acoes_por_cargo), 
    })
