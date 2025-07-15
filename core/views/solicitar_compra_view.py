from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.form import SolicitacaoCompraForm

@login_required
def solicitar_compra(request):
    if request.user.user_type not in ['funcionario', 'gerente']:
        messages.error(request, "Você não tem permissão para solicitar compras.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SolicitacaoCompraForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.criado_por = request.user
            solicitacao.status = 'pendente'
            solicitacao.save()
            messages.success(request, "Solicitação de compra enviada com sucesso.")
            return redirect('dashboard')
    else:
        initial = {
            'tipo_item': request.GET.get('tipo_item'),
            'item_id': request.GET.get('item_id'),
            'destino': request.GET.get('local')
        }
        form = SolicitacaoCompraForm(initial=initial)

    return render(request, 'core/solicitar_compra.html', {'form': form})