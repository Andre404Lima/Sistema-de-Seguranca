from collections import defaultdict
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from core.form import UserCreationFormCustom
from core.models.acao_user import AcaoUsuario
from core.models.user import CustomUser


class ControleUsuariosView(LoginRequiredMixin, View):
    # exibe as últimas 50 ações
    def get(self, request):
        # Pega permissões e tipos permitidos do usuário logado
        pode_criar, tipos_permitidos, usuarios, base_qs = request.user.get_permissoes()

        # lista últimas 50 ações
        base_qs = base_qs.order_by('-data_hora')[:50] 
        acoes_por_cargo = defaultdict(list)
        for acao in base_qs:
            acoes_por_cargo[acao.usuario.user_type].append({
                'usuario_nome': acao.usuario.username,
                'acao': acao.acao,
                'data_hora': acao.data_hora,
            }) 

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
        pode_criar, _, tipos_permitidos, usuarios, base_qs = request.user.get_permissoes()
        # Pega permissões e tipos permitidos do usuário logado

        if not pode_criar or not tipos_permitidos:
            return HttpResponseForbidden("Sem permissão para criar usuários.")

        form = UserCreationFormCustom(request.POST, tipos_permitidos=tipos_permitidos)

        if form.is_valid():
            # Salva novo usuário e registra ação
            novo_usuario = form.save()
            AcaoUsuario.objects.create(
                usuario=request.user,
                acao=f"Usuário '{novo_usuario.username}' criado com tipo '{novo_usuario.user_type}'"
            )
            return redirect('controle_usuarios')

        base_qs = base_qs.order_by('-data_hora')[:50] # Se formulário inválido, agrupa últimas ações por tipo de usuário
        acoes_por_cargo = defaultdict(list)
        for acao in base_qs:
            acoes_por_cargo[acao.usuario.user_type].append({
                'usuario_nome': acao.usuario.username,
                'acao': acao.acao,
                'data_hora': acao.data_hora,
            })

        # Recarrega página com erros do formulário
        return render(request, 'core/controle_usuarios.html', {
            'usuarios': usuarios,
            'pode_criar': True,
            'form': form,
            'acoes_por_cargo': dict(acoes_por_cargo),
        })


    def _desativar_usuario(self, request):
        user_id = request.POST.get('user_id')
        current_user = request.user

        # Pega flag de desativação do usuário logado
        _, pode_desativar, _, _, _ = current_user.get_permissoes()

        # Bloqueia se usuário não tiver permissão
        if not pode_desativar:
            return HttpResponseForbidden("Sem permissão para desativar usuários.")

        # Busca usuário a ser desativado
        usuario = get_object_or_404(CustomUser, pk=user_id)

        # Impede administrador de desativar usuários superiores
        if current_user.user_type == 'administrador' and usuario.user_type in ['batman', 'alfred']:
            return HttpResponseForbidden("Administrador não pode desativar usuários Batman ou Alfred.")

        # Impede auto-desativação
        if usuario == current_user:
            return HttpResponseForbidden("Você não pode desativar seu próprio usuário.")

        # Desativa usuário e registra ação
        usuario.is_active = False
        usuario.save()

        AcaoUsuario.objects.create(
            usuario=current_user,
            acao=f"Desativou o usuário '{usuario.username}'"
        )

        return redirect('controle_usuarios')



