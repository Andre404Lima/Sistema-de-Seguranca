from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Dispositivo, Equipamento, Veiculo
from core.models.acao_user import AcaoUsuario
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.veiculo import EstoqueVeiculo
from core.models.requisicao import RequisicaoMovimentacao
from core.form import RequisicaoMovimentacaoForm

@login_required
def solicitar_movimentacao(request):
    if request.method == 'POST':
        form = RequisicaoMovimentacaoForm(request.POST)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.criado_por = request.user
            requisicao.solicitante = request.user
            tipo = requisicao.tipo_item
            objeto_id = requisicao.item_id
            origem = requisicao.origem
            destino = requisicao.destino
            qtd = requisicao.quantidade

            MODELOS = {
                'dispositivo': (Dispositivo, EstoqueDispositivo, 'dispositivo'),
                'equipamento': (Equipamento, EstoqueEquipamento, 'equipamento'),
                'veiculo': (Veiculo, EstoqueVeiculo, 'veiculo'),
            }

            if tipo not in MODELOS:
                return HttpResponseForbidden('Tipo de objeto inválido.')

            modelo, estoque_modelo, fk_nome = MODELOS[tipo]
            objeto = get_object_or_404(modelo, id=objeto_id)
            filtro_base = {f'{fk_nome}_id': objeto_id}

            try:
                estoque_origem = estoque_modelo.objects.get(**filtro_base, localizacao=origem)

                if estoque_origem.quantidade < qtd:
                    messages.error(request, 'Quantidade insuficiente no estoque de origem.')
                    return redirect('dashboard')

                if request.user.user_type in ['batman', 'alfred', 'gerente', 'administrador']:
                    estoque_destino, _ = estoque_modelo.objects.get_or_create(
                        **filtro_base, localizacao=destino,
                        defaults={'quantidade': 0}
                    )

                    estoque_origem.quantidade -= qtd
                    estoque_destino.quantidade += qtd
                    estoque_origem.save()
                    estoque_destino.save()

                    requisicao.status = 'autorizada'
                    requisicao.save()

                    messages.success(request, 'Movimentação registrada com sucesso.')
                else:
                    requisicao.status = 'pendente'
                    requisicao.save()

                    messages.info(request, 'Requisição registrada e enviada para aprovação.')

                return redirect('dashboard')

            except estoque_modelo.DoesNotExist:
                messages.error(request, 'Estoque de origem não encontrado.')
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

    tipo = requisicao.tipo_item  
    item_id = requisicao.item_id
    qtd = requisicao.quantidade
    origem = requisicao.origem  
    destino = requisicao.destino  

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
    requisicao.autorizador = user 
    requisicao.save()

    AcaoUsuario.objects.create(
        usuario=user,
        acao=f"Aprovou movimentação de {qtd} {tipo}(s) de {origem} para {destino} (ID do item: {item_id})"
    )

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
        requisicao.autorizador = request.user
        requisicao.save()
        messages.info(request, "Requisição rejeitada.")
    
    return redirect('dashboard')

