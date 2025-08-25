from collections import defaultdict
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from core.form import UserCreationFormCustom
from core.models.acao_user import AcaoUsuario
from core.models.user import CustomUser


class ControleUsuariosView(LoginRequiredMixin, View):
    def get(self, request):
        # Exibe a tela de controle de usuários com base no tipo de usuário logado.
        user_type = request.user.user_type

        # Define permissões e escopo de visualização conforme tipo de usuário
        if user_type == 'funcionario':
            base_qs = AcaoUsuario.objects.filter(usuario__user_type='funcionario')
            pode_criar = False
            tipos_permitidos = []
            usuarios = CustomUser.objects.none()

        elif user_type == 'gerente':
            base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente'])
            pode_criar = False
            tipos_permitidos = []
            usuarios = CustomUser.objects.filter(user_type__in=['funcionario', 'gerente'], is_active=True)

        elif user_type == 'administrador':
            base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente', 'administrador'])
            pode_criar = True
            tipos_permitidos = ['funcionario', 'gerente', 'administrador']
            usuarios = CustomUser.objects.filter(user_type__in=tipos_permitidos, is_active=True)

        elif user_type in ['batman', 'alfred']:
            base_qs = AcaoUsuario.objects.all()
            pode_criar = (user_type == 'batman')  # Só o Batman pode criar usuários desse nível
            tipos_permitidos = ['funcionario', 'gerente', 'administrador', 'batman', 'alfred']
            usuarios = CustomUser.objects.filter(is_active=True)

        else:
            base_qs = AcaoUsuario.objects.none()
            pode_criar = False
            tipos_permitidos = []
            usuarios = CustomUser.objects.none()

        # Coleta últimas 50 ações e agrupa por tipo de usuário
        base_qs = base_qs.order_by('-data_hora')[:50]
        acoes_por_cargo = defaultdict(list)
        for acao in base_qs:
            acoes_por_cargo[acao.usuario.user_type].append({
                'usuario_nome': acao.usuario.username,
                'acao': acao.acao,
                'data_hora': acao.data_hora,
            })

        # Inicializa o formulário de criação, mesmo se for só para exibir
        form = UserCreationFormCustom(tipos_permitidos=tipos_permitidos)

        return render(request, 'core/controle_usuarios.html', {
            'usuarios': usuarios,
            'pode_criar': pode_criar,
            'form': form,
            'acoes_por_cargo': dict(acoes_por_cargo),
        })

    def post(self, request):
        # Trata POSTs para criação ou desativação de usuários
        acao = request.POST.get('acao')

        if acao == 'criar':
            return self._criar_usuario(request)

        elif acao == 'desativar':
            return self._desativar_usuario(request)

        return HttpResponseForbidden("Ação inválida.")

    def _criar_usuario(self, request):
        # Cria um novo usuário, respeitando os tipos permitidos por quem está logado
        user_type = request.user.user_type

        if user_type == 'administrador':
            tipos_permitidos = ['funcionario', 'gerente', 'administrador']
        elif user_type == 'batman':
            tipos_permitidos = ['funcionario', 'gerente', 'administrador', 'batman', 'alfred']
        else:
            return HttpResponseForbidden("Sem permissão para criar usuários.")

        form = UserCreationFormCustom(request.POST, tipos_permitidos=tipos_permitidos)

        if form.is_valid():
            novo_usuario = form.save()
            # Registra ação de criação
            AcaoUsuario.objects.create(
                usuario=request.user,
                acao=f"Usuário '{novo_usuario.username}' criado com tipo '{novo_usuario.user_type}'"
            )
            return redirect('controle_usuarios')

        # Se inválido, recarrega a tela com erros
        usuarios = CustomUser.objects.filter(user_type__in=tipos_permitidos, is_active=True)
        base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=tipos_permitidos).order_by('-data_hora')[:50]

        acoes_por_cargo = defaultdict(list)
        for acao in base_qs:
            acoes_por_cargo[acao.usuario.user_type].append({
                'usuario_nome': acao.usuario.username,
                'acao': acao.acao,
                'data_hora': acao.data_hora,
            })

        return render(request, 'core/controle_usuarios.html', {
            'usuarios': usuarios,
            'pode_criar': True,
            'form': form,
            'acoes_por_cargo': dict(acoes_por_cargo),
        })

    def _desativar_usuario(self, request):
        # Desativa um usuário com base nas permissões do usuário logado
        user_id = request.POST.get('user_id')
        current_user = request.user
        current_type = current_user.user_type

        if current_type not in ['administrador', 'batman', 'alfred']:
            return HttpResponseForbidden("Você não tem permissão para desativar usuários.")

        usuario = get_object_or_404(CustomUser, pk=user_id)

        # Impede que administradores desativem usuários de nível superior
        if current_type == 'administrador' and usuario.user_type in ['batman', 'alfred']:
            return HttpResponseForbidden("Administrador não pode desativar usuários Batman ou Alfred.")

        if usuario == current_user:
            return HttpResponseForbidden("Você não pode desativar seu próprio usuário.")

        usuario.is_active = False
        usuario.save()

        # Registra a ação de desativação
        AcaoUsuario.objects.create(
            usuario=current_user,
            acao=f"Desativou o usuário '{usuario.username}'"
        )

        return redirect('controle_usuarios')
