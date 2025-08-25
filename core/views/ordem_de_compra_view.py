from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.form import OrdemCompraForm
from core.models.acao_user import AcaoUsuario
from core.models.compra import SolicitacaoCompra, OrdemCompra
from core.models.dispositivo import Dispositivo, EstoqueDispositivo
from core.models.equipamento import Equipamento, EstoqueEquipamento
from core.models.veiculo import Veiculo, EstoqueVeiculo

# ---------------------- FUNÇÕES AUXILIARES ----------------------

def get_item_obj(tipo, item_id):
    # Retorna o objeto do item correspondente ao tipo e ID
    if tipo == 'dispositivo':
        return Dispositivo.objects.filter(id=item_id).first()
    elif tipo == 'equipamento':
        return Equipamento.objects.filter(id=item_id).first()
    elif tipo == 'veiculo':
        return Veiculo.objects.filter(id=item_id).first()
    return None

def atualizar_estoque(tipo, item_obj, local, quantidade):
    # Atualiza o estoque do item no local especificado
    if tipo == 'dispositivo':
        estoque, _ = EstoqueDispositivo.objects.get_or_create(
            dispositivo=item_obj, localizacao=local, defaults={'quantidade': 0}
        )
    elif tipo == 'equipamento':
        estoque, _ = EstoqueEquipamento.objects.get_or_create(
            equipamento=item_obj, localizacao=local, defaults={'quantidade': 0}
        )
    elif tipo == 'veiculo':
        estoque, _ = EstoqueVeiculo.objects.get_or_create(
            veiculo=item_obj, localizacao=local, defaults={'quantidade': 0}
        )
    else:
        return False
    estoque.quantidade += quantidade
    estoque.save()
    return True

# ---------------------- AUTORIZAR SOLICITAÇÃO ----------------------

class AutorizarSolicitacaoCompraView(LoginRequiredMixin, View):
    def get(self, request, solicitacao_id):
        # Autorização de solicitação, criando ordem de compra correspondente
        user = request.user
        if user.user_type != 'gerente':
            messages.error(request, "Você não tem permissão para autorizar solicitações.")
            return redirect('dashboard')

        solicitacao = get_object_or_404(SolicitacaoCompra, pk=solicitacao_id)
        if solicitacao.status != 'pendente':
            messages.warning(request, "Solicitação já foi processada.")
            return redirect('dashboard')

        ordem = OrdemCompra.objects.create(
            origem=solicitacao,
            criado_por=solicitacao.criado_por,
            autorizado_por=user,
            tipo_item=solicitacao.tipo_item,
            item_id=solicitacao.item_id,
            quantidade=solicitacao.quantidade,
            destino=solicitacao.destino,
            status='autorizada',
        )
        solicitacao.status = 'convertida'  # Marca a solicitação como processada
        solicitacao.save()

        messages.success(request, f"Solicitação autorizada e Ordem de Compra #{ordem.id} criada.")
        return redirect('dashboard')

# ---------------------- NEGAR SOLICITAÇÃO ----------------------

class NegarSolicitacaoCompraView(LoginRequiredMixin, View):
    def get(self, request, solicitacao_id):
        # Negação de solicitação de compra
        user = request.user
        if user.user_type != 'gerente':
            messages.error(request, "Você não tem permissão para negar solicitações.")
            return redirect('dashboard')

        solicitacao = get_object_or_404(SolicitacaoCompra, pk=solicitacao_id)
        if solicitacao.status != 'pendente':
            messages.warning(request, "Solicitação já foi processada.")
            return redirect('dashboard')

        solicitacao.status = 'negada'
        solicitacao.save()
        messages.success(request, "Solicitação negada com sucesso.")
        return redirect('dashboard')

# ---------------------- CRIAR ORDEM DE COMPRA ----------------------

class CriarOrdemCompraDiretaView(LoginRequiredMixin, View):
    def get(self, request):
        # Exibe formulário para criar ordem de compra direta
        form = OrdemCompraForm()
        return render(request, 'core/criar_ordem_compra.html', {'form': form})

    def post(self, request):
        # Processa criação de ordem de compra direta
        user = request.user
        if user.user_type not in ['gerente', 'administrador', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão para criar ordens de compra diretas.")
            return redirect('dashboard')

        form = OrdemCompraForm(request.POST)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.criado_por = user
            ordem.status = 'autorizada'
            ordem.save()

            if user.user_type in ['administrador', 'batman', 'alfred']:
                # Usuários especiais podem pagar a ordem imediatamente
                ordem.status = 'paga'
                ordem.realizado_por = user
                ordem.data_realizacao = timezone.now()
                ordem.save()

                item = get_item_obj(ordem.tipo_item, ordem.item_id)
                if item and atualizar_estoque(ordem.tipo_item, item, ordem.destino, ordem.quantidade):
                    messages.success(request, f"Ordem de compra x{ordem.quantidade} ({ordem.get_item_nome()}) paga com sucesso.")
                else:
                    messages.error(request, f"Erro ao atualizar estoque para item ID {ordem.item_id}.")
                return redirect('dashboard')

            messages.success(request, f"Ordem de compra criada com sucesso e aguardando pagamento.")
            return redirect('dashboard')

        return render(request, 'core/criar_ordem_compra.html', {'form': form})

# ---------------------- PAGAR ORDEM ----------------------

class PagarOrdemCompraView(LoginRequiredMixin, View):
    def get(self, request, ordem_id):
        # Pagamento de ordem de compra e atualização do estoque
        user = request.user
        if user.user_type not in ['administrador', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão para realizar essa ordem.")
            return redirect('dashboard')

        ordem = get_object_or_404(OrdemCompra, id=ordem_id)
        if user.user_type == 'alfred' and not ordem.destino.startswith('SECRETO'):
            messages.error(request, "Alfred só pode pagar ordens com destino secreto.")
            return redirect('dashboard')

        if ordem.status != 'autorizada':
            messages.warning(request, "Esta ordem não está autorizada para pagamento.")
            return redirect('dashboard')

        ordem.status = 'paga'
        ordem.realizado_por = user
        ordem.data_realizacao = timezone.now()
        ordem.save()

        # Registra ação do usuário
        AcaoUsuario.objects.create(
            usuario=request.user,
            acao=f'Ordem de compra #{ordem.id} paga.',
            data_hora=timezone.now()
        )

        item = get_item_obj(ordem.tipo_item, ordem.item_id)
        if item and atualizar_estoque(ordem.tipo_item, item, ordem.destino, ordem.quantidade):
            messages.success(request, "Ordem de compra paga e estoque atualizado com sucesso.")
        else:
            messages.error(request, "Erro ao atualizar estoque: item não encontrado.")
        return redirect('dashboard')

# ---------------------- NEGAR ORDEM ----------------------

class NegarOrdemCompraView(LoginRequiredMixin, View):
    def get(self, request, ordem_id):
        # Negação de ordem de compra autorizada
        user = request.user
        if user.user_type not in ['administrador', 'batman']:
            messages.error(request, "Você não tem permissão para negar essa ordem.")
            return redirect('dashboard')

        ordem = get_object_or_404(OrdemCompra, id=ordem_id)
        if ordem.status != 'autorizada':
            messages.warning(request, "Esta ordem não está autorizada e não pode ser negada.")
            return redirect('dashboard')

        ordem.status = 'negada'
        ordem.realizado_por = user
        ordem.data_realizacao = timezone.now()
        ordem.save()
        messages.success(request, "Ordem de compra negada com sucesso.")
        return redirect('dashboard')
