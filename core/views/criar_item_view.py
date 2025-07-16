from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Dispositivo, Equipamento, Veiculo
from core.form import DispositivoForm, EquipamentoForm, VeiculoForm

@login_required
def criar_item(request, tipo):
    if request.user.user_type not in ['administrador', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para criar itens.")
        return redirect('dashboard')

    FORMULARIOS = {
        'dispositivo': DispositivoForm,
        'equipamento': EquipamentoForm,
        'veiculo': VeiculoForm,
    }

    if tipo not in FORMULARIOS:
        messages.error(request, "Tipo de item inválido.")
        return redirect('dashboard')

    form_class = FORMULARIOS[tipo]
    form = form_class(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"{tipo.capitalize()} criado com sucesso.")
            return redirect(f'lista_{tipo}s')

    return render(request, 'core/form_item.html', {
        'form': form,
        'titulo': f"Criar {tipo.capitalize()}",
    })
