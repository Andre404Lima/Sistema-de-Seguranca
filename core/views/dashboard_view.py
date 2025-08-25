import unicodedata
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models.manutencao import RequisicaoManutencao
from core.models.requisicao import RequisicaoMovimentacao
from core.models import AcaoUsuario
from core.models.compra import SolicitacaoCompra, OrdemCompra
from core.constants import LOCALIZACAO_CHOICES
from core.form import UserCreationFormCustom


def formatar_nome_imagem(nome):
    # Remove acentos e caracteres especiais de nomes para gerar nomes de arquivos seguros.
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    return ''.join(c for c in nome_sem_acento if c.isalnum())


class DashboardView(LoginRequiredMixin, View):
    # Exibe o painel principal (dashboard), com controle de requisições, ações e criação de usuários.
    def get(self, request):
        return self._render_dashboard(request)

    def post(self, request):
        return self._render_dashboard(request)

    def _render_dashboard(self, request):
        user = request.user

        # Coleta de dados
        requisicoes_manut = RequisicaoManutencao.objects.filter(
            status__in=['pendente', 'em_manutencao', 'autorizada']
        )
        solicitacoes_compra = SolicitacaoCompra.objects.filter(status='pendente')
        ordens_compra = OrdemCompra.objects.filter(status='autorizada')
        requisicoes_movimentacao = RequisicaoMovimentacao.objects.filter(status='pendente')

        # Agrupar requisições pendentes
        requisicoes_pendentes = [
            {'tipo': 'manutencao', 'obj': m} for m in requisicoes_manut
        ] + [
            {'tipo': 'movimentacao', 'obj': m} for m in requisicoes_movimentacao
        ]

        if user.user_type in ['gerente', 'funcionario']:
            requisicoes_pendentes += [{'tipo': 'compra', 'obj': s} for s in solicitacoes_compra]

        if user.user_type in ['gerente', 'administrador', 'batman', 'alfred']:
            requisicoes_pendentes += [{'tipo': 'ordem', 'obj': o} for o in ordens_compra]

        # Ordenar por data
        requisicoes_pendentes.sort(key=lambda x: getattr(x['obj'], 'data_criacao', None) or '')

        # Locais formatados para exibição
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

        # Permissões e ações de usuário
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

        # Formatar ações
        acoes = acoes.order_by('-data_hora')[:50]
        acoes_formatadas = [{
            'usuario_nome': acao.usuario.username,
            'usuario_tipo': acao.usuario.user_type,
            'acao': acao.acao,
            'data_hora': acao.data_hora,
        } for acao in acoes]

        # Formulário de criação de usuário (somente para quem pode)
        form = None
        if pode_criar:
            if request.method == 'POST':
                form = UserCreationFormCustom(request.POST, tipos_permitidos=tipos_permitidos)
                if form.is_valid():
                    form.save()
                    return redirect('dashboard')
            else:
                form = UserCreationFormCustom(tipos_permitidos=tipos_permitidos)

        # Renderizar template
        return render(request, 'core/dashboard.html', {
            'requisicoes_pendentes': requisicoes_pendentes,
            'user_type': user.user_type,
            'locais_publicos': locais_publicos_formatados,
            'locais_secretos': locais_secretos_formatados,
            'acoes_usuarios': acoes_formatadas,
            'pode_criar_user': pode_criar,
            'form': form,
        })
