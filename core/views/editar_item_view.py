from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import Dispositivo, Equipamento, Veiculo
from core.form import DispositivoForm, EquipamentoForm, VeiculoForm


@login_required
def editar_item(request, tipo, pk):
    if request.user.user_type not in ['administrador', 'batman', 'alfred']:
        messages.error(request, "Você não tem permissão para editar itens.")
        return redirect('dashboard')

    MODELOS = {
        'dispositivo': (Dispositivo, DispositivoForm),
        'equipamento': (Equipamento, EquipamentoForm),
        'veiculo': (Veiculo, VeiculoForm),
    }

    if tipo not in MODELOS:
        messages.error(request, "Tipo de item inválido.")
        return redirect('dashboard')

    modelo, form_class = MODELOS[tipo]
    instancia = get_object_or_404(modelo, pk=pk)
    form = form_class(request.POST or None, request.FILES or None, instance=instancia)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"{tipo.capitalize()} editado com sucesso.")
            return redirect(f'lista_{tipo}s')

    return render(request, 'core/form_item.html', {
        'form': form,
        'titulo': f"Editar {tipo.capitalize()}",
    })
