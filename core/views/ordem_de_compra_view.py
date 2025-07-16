from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.form import OrdemCompraForm
from core.models.compra import SolicitacaoCompra, OrdemCompra
from core.models.dispositivo import Dispositivo, EstoqueDispositivo
from core.models.equipamento import Equipamento, EstoqueEquipamento
from core.models.veiculo import Veiculo, EstoqueVeiculo

# ---------------------- FUNÇÕES AUXILIARES ----------------------

def get_item_obj(tipo, item_id):
    if tipo == 'dispositivo':
        return Dispositivo.objects.filter(id=item_id).first()
    elif tipo == 'equipamento':
        return Equipamento.objects.filter(id=item_id).first()
    elif tipo == 'veiculo':
        return Veiculo.objects.filter(id=item_id).first()
    return None

def atualizar_estoque(tipo, item_obj, local, quantidade):
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

@login_required
def autorizar_solicitacao_compra(request, solicitacao_id):
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
    solicitacao.status = 'convertida'
    solicitacao.save()

    messages.success(request, f"Solicitação autorizada e Ordem de Compra #{ordem.id} criada.")
    return redirect('dashboard')

# ---------------------- NEGAR SOLICITAÇÃO ----------------------

@login_required
def negar_solicitacao_compra(request, solicitacao_id):
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

@login_required
def criar_ordem_compra_direta(request):
    user = request.user
    if user.user_type not in ['gerente', 'administrador', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para criar ordens de compra diretas.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = OrdemCompraForm(request.POST)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.criado_por = user
            ordem.status = 'autorizada'
            ordem.save()

            # Se já for administrador, a ordem será paga automaticamente
            if user.user_type in ['administrador', 'batman', 'alfred']:
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
    else:
        form = OrdemCompraForm()

    return render(request, 'core/criar_ordem_compra.html', {'form': form})

# ---------------------- PAGAR ORDEM ----------------------

@login_required
def pagar_ordem_compra(request, ordem_id):
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

    item = get_item_obj(ordem.tipo_item, ordem.item_id)
    if item and atualizar_estoque(ordem.tipo_item, item, ordem.destino, ordem.quantidade):
        messages.success(request, "Ordem de compra paga e estoque atualizado com sucesso.")
    else:
        messages.error(request, "Erro ao atualizar estoque: item não encontrado.")
    return redirect('dashboard')

# ---------------------- NEGAR ORDEM ----------------------

@login_required
def negar_ordem_compra(request, ordem_id):
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
