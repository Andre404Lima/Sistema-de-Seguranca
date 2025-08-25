from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Dispositivo, Equipamento, Veiculo
from core.models.acao_user import AcaoUsuario
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.veiculo import EstoqueVeiculo
from core.models.requisicao import RequisicaoMovimentacao
from core.form import RequisicaoMovimentacaoForm

#-------------------------solicitarMovimentacao---------------------------------------------------
class SolicitarMovimentacaoView(LoginRequiredMixin, FormView):
    template_name = "core/solicitar_movimentacao.html"
    form_class = RequisicaoMovimentacaoForm
    success_url = "/dashboard/"  # redireciona após concluir

    def form_valid(self, form):
        requisicao = form.save(commit=False)
        requisicao.criado_por = self.request.user
        requisicao.solicitante = self.request.user

        # dados da requisição
        tipo = requisicao.tipo_item
        objeto_id = requisicao.item_id
        origem = requisicao.origem
        destino = requisicao.destino
        qtd = requisicao.quantidade

        # mapeamento de tipos para modelos
        MODELOS = {
            'dispositivo': (Dispositivo, EstoqueDispositivo, 'dispositivo'),
            'equipamento': (Equipamento, EstoqueEquipamento, 'equipamento'),
            'veiculo': (Veiculo, EstoqueVeiculo, 'veiculo'),
        }

        if tipo not in MODELOS:
            return HttpResponseForbidden('Tipo de objeto inválido.')

        # recupera o modelo correto
        modelo, estoque_modelo, fk_nome = MODELOS[tipo]
        objeto = get_object_or_404(modelo, id=objeto_id)
        filtro_base = {f'{fk_nome}_id': objeto_id}

        try:
            # verifica estoque de origem
            estoque_origem = estoque_modelo.objects.get(**filtro_base, localizacao=origem)

            if estoque_origem.quantidade < qtd:
                messages.error(self.request, 'Quantidade insuficiente no estoque de origem.')
                return redirect(self.success_url)

            # usuários com poder aprovam e movimentam direto
            if self.request.user.user_type in ['batman', 'alfred', 'gerente', 'administrador']:
                estoque_destino, _ = estoque_modelo.objects.get_or_create(
                    **filtro_base, localizacao=destino,
                    defaults={'quantidade': 0}
                )

                # movimenta quantidades
                estoque_origem.quantidade -= qtd
                estoque_destino.quantidade += qtd
                estoque_origem.save()
                estoque_destino.save()

                requisicao.status = 'autorizada'
                requisicao.save()

                messages.success(self.request, 'Movimentação registrada com sucesso.')
            else:
                # se não tiver permissão → pendente
                requisicao.status = 'pendente'
                requisicao.save()

                messages.info(self.request, 'Requisição registrada e enviada para aprovação.')

            return redirect(self.success_url)

        except estoque_modelo.DoesNotExist:
            messages.error(self.request, 'Estoque de origem não encontrado.')
            return redirect(self.success_url)

#-------------------------autorizarMovimentacao---------------------------------------------------
class AutorizarRequisicaoView(LoginRequiredMixin, View):
    def post(self, request, req_id):
        # valida permissão
        user = request.user
        if user.user_type not in ['gerente', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão para autorizar.")
            return redirect(self.success_url)

        requisicao = get_object_or_404(RequisicaoMovimentacao, pk=req_id)

        # só pode autorizar pendentes
        if requisicao.status != 'pendente':
            messages.warning(request, "Requisição já foi processada.")
            return redirect(self.success_url)

        # dados da requisição
        tipo = requisicao.tipo_item  
        item_id = requisicao.item_id
        qtd = requisicao.quantidade
        origem = requisicao.origem  
        destino = requisicao.destino  

        # seleciona modelo de estoque
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
            return redirect(self.success_url)

        # valida estoque de origem
        origem_estoque = estoque_model.objects.filter(localizacao=origem, **filtro).first()
        if not origem_estoque or origem_estoque.quantidade < qtd:
            messages.error(request, "Estoque insuficiente na origem.")
            return redirect(self.success_url)

        # movimenta quantidades
        origem_estoque.quantidade -= qtd
        origem_estoque.save()

        destino_estoque, _ = estoque_model.objects.get_or_create(localizacao=destino, **filtro)
        destino_estoque.quantidade += qtd
        destino_estoque.save()

        # atualiza status
        requisicao.status = 'autorizada'
        requisicao.autorizador = user 
        requisicao.save()

        # registra ação do usuário
        AcaoUsuario.objects.create(
            usuario=user,
            acao=f"Aprovou movimentação de {qtd} {tipo}(s) de {origem} para {destino} (ID do item: {item_id})"
        )

        messages.success(request, "Requisição autorizada com sucesso.")
        return redirect('dashboard')

#---------------------------NegarMovimentacao---------------------------------------------------
class RejeitarRequisicaoView(LoginRequiredMixin, View):
    success_url = "/dashboard/"

    def post(self, request, pk):
        # valida permissão
        if request.user.user_type not in ['gerente', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão.")
            return redirect(self.success_url)

        requisicao = get_object_or_404(RequisicaoMovimentacao, pk=pk)

        # só rejeita se estiver pendente
        if requisicao.status == 'pendente':
            requisicao.status = 'rejeitada'
            requisicao.autorizador = request.user
            requisicao.save()
            messages.info(request, "Requisição rejeitada.")
        
        return redirect(self.success_url)

