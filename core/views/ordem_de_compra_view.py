from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.form import OrdemCompraForm
from core.models.compra import SolicitacaoCompra, OrdemCompra
from core.models.dispositivo import Dispositivo, EstoqueDispositivo
from core.models.equipamento import Equipamento
from core.models.requisicao import User
from core.models.veiculo import Veiculo

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

    solicitacao.status = 'autorizada'
    solicitacao.save()

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
# ---------------------------NEGAR SOLICITAÇÃO DE ORDEM DE COMPRA -------------------------------------------------------------------
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
# ---------------------------CRIAR ORDEM DE COMPRA -------------------------------------------------------------------
@login_required
def criar_ordem_compra_direta(request):
    user = request.user
    if user.user_type != 'gerente' and user.user_type not in ['administrador', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para criar ordens de compra diretas.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = OrdemCompraForm(request.POST)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.criado_por = user
            ordem.status = 'autorizada'  
            ordem.save()

            # Se o usuário for admin, batman ou alfred, paga a ordem automaticamente
            if user.user_type in ['administrador', 'batman', 'alfred']:
                ordem.status = 'paga'
                ordem.realizado_por = user
                ordem.data_realizacao = timezone.now()
                ordem.save()

                # Atualizar estoque automaticamente (replicando lógica do pagar_ordem_compra)
                item_obj = None
                if ordem.tipo_item == 'dispositivo':
                    item_obj = Dispositivo.objects.filter(id=ordem.item_id).first()
                elif ordem.tipo_item == 'equipamento':
                    item_obj = Equipamento.objects.filter(id=ordem.item_id).first()
                elif ordem.tipo_item == 'veiculo':
                    item_obj = Veiculo.objects.filter(id=ordem.item_id).first()

                if item_obj:
                    if ordem.tipo_item == 'dispositivo':
                        estoque, created = EstoqueDispositivo.objects.get_or_create(
                            dispositivo=item_obj,
                            localizacao=ordem.destino,
                            defaults={'quantidade': 0}
                        )
                        estoque.quantidade += ordem.quantidade
                        estoque.save()

                    # Repita para equipamento e veículo se necessário

                messages.success(request, f"Ordem de compra de x{ordem.quantidade} ({ordem.get_item_nome()})  paga com sucesso.")
            else:
                messages.error(request, f"Ordem de compra {ordem.item} {ordem.quantidade} não pode ser paga.")

            return redirect('dashboard')
    else:
        form = OrdemCompraForm()

    return render(request, 'core/criar_ordem_compra.html', {'form': form})
# ---------------------------PAGAR ORDEM DE COMPRA -------------------------------------------------------------------
@login_required
def pagar_ordem_compra(request, ordem_id):
    user = request.user

    # Valida permissões...
    if user.user_type not in ['administrador', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para realizar essa ordem.")
        return redirect('dashboard')

    ordem = get_object_or_404(OrdemCompra, id=ordem_id)

    # Restrições específicas
    if user.user_type == 'alfred' and not ordem.destino.startswith('SECRETO'):
        messages.error(request, "Alfred só pode pagar ordens com destino secreto.")
        return redirect('dashboard')

    if ordem.status != 'autorizada':
        messages.warning(request, "Esta ordem não está autorizada para pagamento.")
        return redirect('dashboard')

    # Atualiza o status da ordem
    ordem.status = 'paga'
    ordem.realizado_por = user
    ordem.data_realizacao = timezone.now()
    ordem.save()

    # --- Atualiza o estoque ---

    # 1. Descobre o tipo de item e busca o objeto correto
    item_obj = None
    if ordem.tipo_item == 'dispositivo':
        item_obj = Dispositivo.objects.filter(id=ordem.item_id).first()
    elif ordem.tipo_item == 'equipamento':
        item_obj = Equipamento.objects.filter(id=ordem.item_id).first()
    elif ordem.tipo_item == 'veiculo':
        item_obj = Veiculo.objects.filter(id=ordem.item_id).first()

    if not item_obj:
        messages.error(request, "Item da ordem não encontrado no sistema.")
        return redirect('dashboard')

    # 2. Busca o estoque do item no destino
    from core.models import EstoqueDispositivo  # Ajuste para seu modelo correto

    # Aqui você deve ajustar para o tipo de estoque conforme o tipo_item:
    # Exemplo só para dispositivo:
    if ordem.tipo_item == 'dispositivo':
        estoque, created = EstoqueDispositivo.objects.get_or_create(
            dispositivo=item_obj,
            localizacao=ordem.destino,
            defaults={'quantidade': 0}
        )
        estoque.quantidade += ordem.quantidade
        estoque.save()

    # Se tiver estoques para equipamento e veículo, repita para eles conforme seu modelo

    messages.success(request, "Ordem de compra paga e estoque atualizado com sucesso.")
    return redirect('dashboard')
# ---------------------------NEGAR ORDEM DE COMPRA -------------------------------------------------------------------
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