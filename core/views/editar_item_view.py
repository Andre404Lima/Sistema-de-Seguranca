from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from core.models import Dispositivo, Equipamento, Veiculo
from core.form import DispositivoForm, EquipamentoForm, VeiculoForm

# Classe para editar dispositivos, equipamentos ou veículos, dependendo do tipo informado
class EditarItemView(LoginRequiredMixin, View):
    # Define quais modelos e formulários estão disponíveis
    MODELOS = {
        'dispositivo': (Dispositivo, DispositivoForm),
        'equipamento': (Equipamento, EquipamentoForm),
        'veiculo': (Veiculo, VeiculoForm),
    }

    def dispatch(self, request, *args, **kwargs):
        # Garante que apenas usuários autorizados possam acessar essa view
        if request.user.user_type not in ['administrador', 'batman', 'alfred']:
            messages.error(request, "Você não tem permissão para editar itens.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, tipo, pk):
        # Verifica se o tipo informado está na lista de modelos válidos
        if tipo not in self.MODELOS:
            messages.error(request, "Tipo de item inválido.")
            return redirect('dashboard')

        modelo, form_class = self.MODELOS[tipo]
        instancia = get_object_or_404(modelo, pk=pk)  # Busca o objeto a ser editado
        form = form_class(instance=instancia)  # Inicializa o formulário com a instância existente

        # Renderiza a página de formulário para edição
        return render(request, 'core/form_item.html', {
            'form': form,
            'titulo': f"Editar {tipo.capitalize()}",
        })

    def post(self, request, tipo, pk):
        # Verifica se o tipo informado é válido
        if tipo not in self.MODELOS:
            messages.error(request, "Tipo de item inválido.")
            return redirect('dashboard')

        modelo, form_class = self.MODELOS[tipo]
        instancia = get_object_or_404(modelo, pk=pk)  # Obtém o objeto do banco de dados
        form = form_class(request.POST, request.FILES, instance=instancia)  # Cria o formulário com os dados enviados

        # Verifica se o formulário é válido e salva as alterações
        if form.is_valid():
            form.save()
            messages.success(request, f"{tipo.capitalize()} editado com sucesso.")
            return redirect(f'lista_{tipo}s')  

        # Em caso de erro, reexibe o formulário com mensagens de erro
        return render(request, 'core/form_item.html', {
            'form': form,
            'titulo': f"Editar {tipo.capitalize()}",
        })
