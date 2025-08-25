from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from core.form import SolicitacaoCompraForm
from django.contrib.auth.mixins import LoginRequiredMixin

class SolicitarCompraView(LoginRequiredMixin, View):
    def get(self, request):
        # Verifica permissão de usuário
        if request.user.user_type not in ['funcionario', 'gerente']:
            messages.error(request, "Você não tem permissão para solicitar compras.")
            return redirect('dashboard')

        # Inicializa o formulário com valores de GET, se houver
        initial = {
            'tipo_item': request.GET.get('tipo_item'),
            'item_id': request.GET.get('item_id'),
            'destino': request.GET.get('local')
        }
        form = SolicitacaoCompraForm(initial=initial)
        return render(request, 'core/solicitar_compra.html', {'form': form})

    def post(self, request):
        # Verifica permissão de usuário
        if request.user.user_type not in ['funcionario', 'gerente']:
            messages.error(request, "Você não tem permissão para solicitar compras.")
            return redirect('dashboard')

        # Processa envio do formulário
        form = SolicitacaoCompraForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.criado_por = request.user
            solicitacao.status = 'pendente'
            solicitacao.save()
            messages.success(request, "Solicitação de compra enviada com sucesso.")
            return redirect('dashboard')

        return render(request, 'core/solicitar_compra.html', {'form': form})