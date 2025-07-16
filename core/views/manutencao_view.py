from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.manutencao import RequisicaoManutencao
from core.models.veiculo import EstoqueVeiculo

@login_required
def solicitar_manutencao(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo_item')
        item_id = request.POST.get('item_id')
        local = request.POST.get('localizacao')
        quantidade = int(request.POST.get('quantidade', 0))

        if quantidade <= 0:
            messages.error(request, "Quantidade deve ser maior que zero.")
            return redirect('itens_por_local', local=local)

        try:
            if request.user.user_type == 'funcionario':
                requisicao = RequisicaoManutencao.objects.create(
                    criado_por=request.user,
                    tipo_item=tipo,
                    item_id=item_id,
                    localizacao=local,
                    quantidade=quantidade,
                    status='pendente'
                )
                messages.success(request, f"{requisicao.get_item_nome()} enviado para aprovação de manutenção.")
            
            elif request.user.user_type == 'gerente':
                requisicao = RequisicaoManutencao.objects.create(
                    criado_por=request.user,
                    tipo_item=tipo,
                    item_id=item_id,
                    localizacao=local,
                    quantidade=quantidade,
                    status='em_manutencao'
                )
                item = requisicao.get_item_obj()
                estoque = None
                if requisicao.tipo_item == 'dispositivo':
                    estoque = EstoqueDispositivo.objects.get(dispositivo=item, localizacao=local)
                elif requisicao.tipo_item == 'equipamento':
                    estoque = EstoqueEquipamento.objects.get(equipamento=item, localizacao=local)
                elif requisicao.tipo_item == 'veiculo':
                    estoque = EstoqueVeiculo.objects.get(veiculo=item, localizacao=local)

                if estoque.quantidade >= quantidade:
                    estoque.quantidade -= quantidade
                    estoque.save()
                    messages.success(request, f"{requisicao.get_item_nome()} enviado direto para manutenção.")
                else:
                    requisicao.delete()
                    messages.error(request, "Quantidade insuficiente em estoque.")
            
            else:
                # Outros usuários (administrador, batman, alfred) - mover direto (mesma lógica do gerente?)
                requisicao = RequisicaoManutencao.objects.create(
                    criado_por=request.user,
                    tipo_item=tipo,
                    item_id=item_id,
                    localizacao=local,
                    quantidade=quantidade,
                    status='em_manutencao'
                )
                item = requisicao.get_item_obj()
                estoque = None
                if requisicao.tipo_item == 'dispositivo':
                    estoque = EstoqueDispositivo.objects.get(dispositivo=item, localizacao=local)
                elif requisicao.tipo_item == 'equipamento':
                    estoque = EstoqueEquipamento.objects.get(equipamento=item, localizacao=local)
                elif requisicao.tipo_item == 'veiculo':
                    estoque = EstoqueVeiculo.objects.get(veiculo=item, localizacao=local)

                if estoque.quantidade >= quantidade:
                    estoque.quantidade -= quantidade
                    estoque.save()
                    messages.success(request, f"{requisicao.get_item_nome()} movido direto para manutenção.")
                else:
                    requisicao.delete()
                    messages.error(request, "Quantidade insuficiente em estoque.")

        except Exception as e:
            messages.error(request, f"Erro ao solicitar manutenção: {e}")

        return redirect('dashboard')

    

# --------------------------APROVAR MANUTENÇÃO-----------------------------------------------------------------------------
@login_required
def aprovar_envio_manutencao(request, manutencao_id):
    if request.user.user_type != 'gerente':
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)

    if requisicao.status != 'pendente':
        messages.warning(request, "Requisição já processada.")
        return redirect('dashboard')

    item = requisicao.get_item_obj()
    if not item:
        messages.error(request, "Item não encontrado.")
        return redirect('dashboard')

    try:
        estoque = None
        if requisicao.tipo_item == 'dispositivo':
            estoque = EstoqueDispositivo.objects.get(dispositivo=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'equipamento':
            estoque = EstoqueEquipamento.objects.get(equipamento=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'veiculo':
            estoque = EstoqueVeiculo.objects.get(veiculo=item, localizacao=requisicao.localizacao)

        if estoque.quantidade >= requisicao.quantidade:
            estoque.quantidade -= requisicao.quantidade
            estoque.save()
            requisicao.status = 'em_manutencao'  
            requisicao.save()
            messages.success(request, f"{requisicao.get_item_nome()} enviado para manutenção.")
        else:
            messages.error(request, "Quantidade insuficiente em estoque.")
    except Exception as e:
        messages.error(request, f"Erro ao aprovar envio: {e}")

    return redirect('dashboard')
# --------------------------NEGAR MANUTENÇÃO-----------------------------------------------------------------------------
@login_required
def negar_manutencao(request, manutencao_id):
    if request.user.user_type != 'gerente':
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)

    if requisicao.status != 'pendente':
        messages.warning(request, "Requisição já processada.")
        return redirect('dashboard')

    requisicao.status = 'negada'
    requisicao.save()
    messages.success(request, f"Requisição de manutenção para {requisicao.get_item_nome()} foi negada.")
    return redirect('dashboard')
# --------------------------MOVER PARA MANUTENÇÃO-----------------------------------------------------------------------------
@login_required
def mover_direto_para_manutencao(request, manutencao_id):
    if request.user.user_type == 'funcionario':
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)
    if requisicao.status != 'pendente':
        messages.warning(request, "Requisição já processada.")
        return redirect('dashboard')

    item = requisicao.get_item_obj()
    if not item:
        messages.error(request, "Item não encontrado.")
        return redirect('dashboard')

    try:
        estoque = None
        if requisicao.tipo_item == 'dispositivo':
            estoque = EstoqueDispositivo.objects.get(dispositivo=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'equipamento':
            estoque = EstoqueEquipamento.objects.get(equipamento=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'veiculo':
            estoque = EstoqueVeiculo.objects.get(veiculo=item, localizacao=requisicao.localizacao)

        if estoque.quantidade >= requisicao.quantidade:
            estoque.quantidade -= requisicao.quantidade
            estoque.save()
            requisicao.status = 'em_manutencao'
            requisicao.save()
            messages.success(request, f"{requisicao.get_item_nome()} movido direto para manutenção.")
        else:
            messages.error(request, "Quantidade insuficiente em estoque.")
    except Exception as e:
        messages.error(request, f"Erro ao mover direto: {e}")

    return redirect('dashboard')
# --------------------------CONCLUIR MANUTENÇÃO-----------------------------------------------------------------------------
@login_required
def concluir_manutencao(request, manutencao_id):
    if request.user.user_type not in ['administrador', 'batman', 'alfred']:
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)

    if requisicao.status != 'em_manutencao':
        messages.warning(request, "Requisição não está em manutenção.")
        return redirect('dashboard')

    item = requisicao.get_item_obj()
    if not item:
        messages.error(request, "Item não encontrado.")
        return redirect('dashboard')

    try:
        if requisicao.tipo_item == 'dispositivo':
            estoque, _ = EstoqueDispositivo.objects.get_or_create(dispositivo=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})
        elif requisicao.tipo_item == 'equipamento':
            estoque, _ = EstoqueEquipamento.objects.get_or_create(equipamento=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})
        elif requisicao.tipo_item == 'veiculo':
            estoque, _ = EstoqueVeiculo.objects.get_or_create(veiculo=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})

        estoque.quantidade += requisicao.quantidade
        estoque.save()
        requisicao.status = 'concluida'
        requisicao.data_conclusao = timezone.now()
        requisicao.save()

        messages.success(request, f"{requisicao.get_item_nome()} retornou da manutenção.")
    except Exception as e:
        messages.error(request, f"Erro ao concluir manutenção: {e}")

    return redirect('dashboard')
