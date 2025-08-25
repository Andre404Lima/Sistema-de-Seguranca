from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.veiculo import EstoqueVeiculo
from core.constants import LOCALIZACAO_CHOICES

# View baseada em classe para exibir os itens por local
class ItensPorLocalView(LoginRequiredMixin, TemplateView):
    template_name = 'core/itens_por_local.html'  # Template que será renderizado
#enviar dados para o template em views
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        local = self.kwargs.get('local')
        nome_local = dict(LOCALIZACAO_CHOICES).get(local, local)
        user_type = self.request.user.user_type
        locais_secretos = [cod for cod, _ in LOCALIZACAO_CHOICES[7:]]

        # Define quais locais o usuário pode visualizar
        localizacoes_visiveis = (
            LOCALIZACAO_CHOICES if user_type in ['batman', 'alfred']
            else [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in locais_secretos]
        )

        # Função auxiliar para filtrar e ordenar os itens de estoque
        def filtro(model, fk_field):
            qs = model.objects.filter(localizacao=local, quantidade__gt=0).select_related(fk_field)

            if user_type not in ['batman', 'alfred']:
                qs = qs.exclude(**{f"{fk_field}__secret": True})

            # Ordena por "nome" ou "modelo" dependendo do tipo de item
            order_field = f"{fk_field}__modelo" if fk_field == "veiculo" else f"{fk_field}__nome"
            return qs.order_by(f"{fk_field}__secret", order_field)

        if local in locais_secretos and user_type not in ['batman', 'alfred']:
            context.update({
                'local': nome_local,
                'dispositivos_estoque': [],
                'equipamentos_estoque': [],
                'veiculos_estoque': [],
                'localizacoes_visiveis': localizacoes_visiveis,
            })
        else:
            context.update({
                'local': nome_local,
                'dispositivos_estoque': filtro(EstoqueDispositivo, 'dispositivo'),
                'equipamentos_estoque': filtro(EstoqueEquipamento, 'equipamento'),
                'veiculos_estoque': filtro(EstoqueVeiculo, 'veiculo'),
                'localizacoes_visiveis': localizacoes_visiveis,
            })

        return context

