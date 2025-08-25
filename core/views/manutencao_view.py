from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.manutencao import RequisicaoManutencao
from core.models.veiculo import EstoqueVeiculo


class SolicitarManutencaoView(LoginRequiredMixin, View):
    def post(self, request):
    # Cria uma requisição de manutenção (pendente ou já em manutenção)
    # Se for gerente/admin já move direto e ajusta estoque
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
            else:
                requisicao = RequisicaoManutencao.objects.create(
                    criado_por=request.user,
                    tipo_item=tipo,
                    item_id=item_id,
                    localizacao=local,
                    quantidade=quantidade,
                    status='em_manutencao'
                )
                item = requisicao.get_item_obj()
                estoque = self.get_estoque(requisicao, item)

                if estoque.quantidade >= quantidade:
                    estoque.quantidade -= quantidade
                    estoque.save()
                    messages.success(request, f"{requisicao.get_item_nome()} enviado direto para manutenção.")
                else:
                    requisicao.delete()
                    messages.error(request, "Quantidade insuficiente em estoque.")
        except Exception as e:
            messages.error(request, f"Erro ao solicitar manutenção: {e}")

        return redirect('dashboard')

    def get_estoque(self, requisicao, item):
    # Retorna o estoque referente ao item e local
        if requisicao.tipo_item == 'dispositivo':
            return EstoqueDispositivo.objects.get(dispositivo=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'equipamento':
            return EstoqueEquipamento.objects.get(equipamento=item, localizacao=requisicao.localizacao)
        elif requisicao.tipo_item == 'veiculo':
            return EstoqueVeiculo.objects.get(veiculo=item, localizacao=requisicao.localizacao)


class AprovarManutencaoView(LoginRequiredMixin, View):
    def post(self, request, manutencao_id):
    # Aprova requisição pendente e envia item para manutenção
        if request.user.user_type != 'gerente':
            messages.error(request, "Permissão negada.")
            return redirect('dashboard')

        requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)
        if requisicao.status != 'pendente':
            messages.warning(request, "Requisição já processada.")
            return redirect('dashboard')

        try:
            item = requisicao.get_item_obj()
            estoque = SolicitarManutencaoView().get_estoque(requisicao, item)

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

    
    def get(self, request, manutencao_id):
    # Redireciona GET para POST para evitar erro
        return self.post(request, manutencao_id)


class NegarManutencaoView(LoginRequiredMixin, View):
    def post(self, request, manutencao_id):
    # Nega uma requisição de manutenção pendente
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

    def get(self, request, manutencao_id):
    # Redireciona GET para POST
        return self.post(request, manutencao_id)


class MoverDiretoParaManutencaoView(LoginRequiredMixin, View):
    def post(self, request, manutencao_id):
    # Move requisição pendente direto para manutenção e ajusta estoque
        if request.user.user_type == 'funcionario':
            messages.error(request, "Permissão negada.")
            return redirect('dashboard')

        requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)
        if requisicao.status != 'pendente':
            messages.warning(request, "Requisição já processada.")
            return redirect('dashboard')

        try:
            item = requisicao.get_item_obj()
            estoque = SolicitarManutencaoView().get_estoque(requisicao, item)

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

    def get(self, request, manutencao_id):
        return self.post(request, manutencao_id)


class ConcluirManutencaoView(LoginRequiredMixin, View):
    def post(self, request, manutencao_id):
        if request.user.user_type not in ['administrador', 'batman', 'alfred']:
            messages.error(request, "Permissão negada.")
            return redirect('dashboard')

        requisicao = get_object_or_404(RequisicaoManutencao, pk=manutencao_id)

        if requisicao.status != 'em_manutencao':
            messages.warning(request, "Requisição não está em manutenção.")
            return redirect('dashboard')

        try:
            item = requisicao.get_item_obj()
            estoque = None
            if requisicao.tipo_item == 'dispositivo':
                estoque, _ = EstoqueDispositivo.objects.get_or_create(
                    dispositivo=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})
            elif requisicao.tipo_item == 'equipamento':
                estoque, _ = EstoqueEquipamento.objects.get_or_create(
                    equipamento=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})
            elif requisicao.tipo_item == 'veiculo':
                estoque, _ = EstoqueVeiculo.objects.get_or_create(
                    veiculo=item, localizacao=requisicao.localizacao, defaults={'quantidade': 0})

            estoque.quantidade += requisicao.quantidade
            estoque.save()
            requisicao.status = 'concluida'
            requisicao.data_conclusao = timezone.now()
            requisicao.save()

            messages.success(request, f"{requisicao.get_item_nome()} retornou da manutenção.")
        except Exception as e:
            messages.error(request, f"Erro ao concluir manutenção: {e}")

        return redirect('dashboard')

    def get(self, request, manutencao_id):
        return self.post(request, manutencao_id)
