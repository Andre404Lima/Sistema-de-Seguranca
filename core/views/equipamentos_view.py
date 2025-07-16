from django.shortcuts import render
from core.constants import LOCALIZACAO_CHOICES
from core.models.equipamento import Equipamento
from django.contrib.auth.decorators import login_required
#---------------------------LOCAIS SECRETOS-----------------------------------------------
LOCALIZACOES_SECRETAS = [
    'BAT_CAVERNA',
    'POSTO_AVANCADO_CENTRO',
    'POSTO_AVANCADO_NORTE',
    'ESTACAO_SUBMERSA_PORTO'
]
# ------------------- EQUIPAMENTOS -------------------------------------------
@login_required
def lista_equipamentos(request):
    base_qs = Equipamento.objects.prefetch_related('estoques').order_by('secret', 'nome')

    if request.user.user_type in ['batman', 'alfred']:
        equipamentos = base_qs
        locais_visiveis = LOCALIZACAO_CHOICES
    else:
        equipamentos = base_qs.filter(secret=False)
        locais_visiveis = [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS]

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    equipamentos_com_dados = []

    for equip in equipamentos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = equip.estoques.all()
        else:
            estoques_visiveis = [
                est for est in equip.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        estoques_visiveis = [est for est in estoques_visiveis if est.quantidade > 0]

        estoques_visiveis = sorted(
            estoques_visiveis,
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            )
        )

        total = sum(est.quantidade for est in estoques_visiveis)

        equipamentos_com_dados.append({
            'obj': equip,
            'estoques': estoques_visiveis,
            'total': total,
        })

    return render(request, 'core/lista_equipamentos.html', {
        'equipamentos': equipamentos_com_dados,
        'localizacoes_visiveis': locais_visiveis,
        'tipo_item': 'equipamento'
    })