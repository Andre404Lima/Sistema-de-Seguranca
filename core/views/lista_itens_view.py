from django.views import View
from django.shortcuts import render
from core.constants import LOCALIZACAO_CHOICES
from core.models.dispositivo import Dispositivo
from core.models.equipamento import Equipamento
from core.models.veiculo import Veiculo

# Locais secretos que usuários comuns não visualizam
LOCALIZACOES_SECRETAS = [
    'BAT_CAVERNA',
    'POSTO_AVANCADO_CENTRO',
    'POSTO_AVANCADO_NORTE',
    'ESTACAO_SUBMERSA_PORTO'
]

class ItensPorCategoriaView(View):
    template_name = 'core/itens_categoria.html'

    def get(self, request, categoria):
        user_type = request.user.user_type
        NOME_LOCAL = dict(LOCALIZACAO_CHOICES)

        # Define modelo de acordo com a categoria
        modelo_map = {
            'dispositivo': Dispositivo,
            'equipamento': Equipamento,
            'veiculo': Veiculo,
        }

        modelo = modelo_map.get(categoria)
        if not modelo:
            return render(request, self.template_name, {
                'itens': [],
                'tipo_item': categoria,
                'localizacoes_visiveis': [],
                'categoria_valida': False,
            })

        # Query base com ordenação e prefetch
        qs = modelo.objects.prefetch_related('estoques').order_by('secret', 'nome' if categoria != 'veiculo' else 'modelo')

        if user_type not in ['batman', 'alfred']:
            qs = qs.filter(secret=False)

        itens_com_dados = []
        for item in qs:
            # Seleciona os estoques visíveis
            if user_type in ['batman', 'alfred']:
                estoques = item.estoques.all()
            else:
                estoques = [est for est in item.estoques.all() if est.localizacao not in LOCALIZACOES_SECRETAS]

            estoques = [est for est in estoques if est.quantidade > 0]

            # Ordena estoques priorizando os não-secretos e nome do local
            estoques.sort(key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            ))

            total = sum(est.quantidade for est in estoques)

            itens_com_dados.append({
                'obj': item,
                'estoques': estoques,
                'total': total,
            })

        # Define locais visíveis conforme o tipo de usuário
        locais_visiveis = LOCALIZACAO_CHOICES if user_type in ['batman', 'alfred'] else [
            loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS
        ]

        return render(request, self.template_name, {
            'itens': itens_com_dados,
            'tipo_item': categoria,
            'localizacoes_visiveis': locais_visiveis,
            'categoria_valida': True,
        })

