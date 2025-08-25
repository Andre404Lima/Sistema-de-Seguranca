from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from core.form import DispositivoForm, EquipamentoForm, VeiculoForm

class CriarItemView(LoginRequiredMixin, View): 
    # Dicionário que mapeia tipos de item para seus respectivos formulários
    FORMULARIOS = {
        'dispositivo': DispositivoForm,
        'equipamento': EquipamentoForm,
        'veiculo': VeiculoForm,
    }

    def dispatch(self, request, *args, **kwargs): 
        # verificação de permissão do usuário.
        if request.user.user_type not in ['administrador', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão para criar itens.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, tipo):
        # Verifica se o tipo de item é válido, e renderiza o formulário vazio correspondente.
        if tipo not in self.FORMULARIOS:
            messages.error(request, "Tipo de item inválido.")
            return redirect('dashboard')

        form_class = self.FORMULARIOS[tipo]
        form = form_class()
        return render(request, 'core/form_item.html', {
            'form': form,
            'titulo': f"Criar {tipo.capitalize()}",
        })

    def post(self, request, tipo):
        # Valida o tipo de item, processa o formulário e salva o objeto no banco de dados.
        if tipo not in self.FORMULARIOS:
            messages.error(request, "Tipo de item inválido.")
            return redirect('dashboard')

        form_class = self.FORMULARIOS[tipo]
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"{tipo.capitalize()} criado com sucesso.")
            return redirect(f'lista_{tipo}s')

        return render(request, 'core/form_item.html', {
            'form': form,
            'titulo': f"Criar {tipo.capitalize()}",
        })
