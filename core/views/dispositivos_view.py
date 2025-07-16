from django.shortcuts import render
from core.constants import LOCALIZACAO_CHOICES
from core.models.dispositivo import Dispositivo
from django.contrib.auth.decorators import login_required
#---------------------------LOCAIS SECRETOS-----------------------------------------------
LOCALIZACOES_SECRETAS = [
    'BAT_CAVERNA',
    'POSTO_AVANCADO_CENTRO',
    'POSTO_AVANCADO_NORTE',
    'ESTACAO_SUBMERSA_PORTO'
]
# ------------------- DISPOSITIVOS -------------------------------------------
@login_required
def lista_dispositivos(request):
    base_qs = Dispositivo.objects.order_by('secret', 'nome')

    if request.user.user_type in ['batman', 'alfred']:
        dispositivos = base_qs
        locais_visiveis = LOCALIZACAO_CHOICES
    else:
        dispositivos = base_qs.filter(secret=False)
        locais_visiveis = [loc for loc in LOCALIZACAO_CHOICES if loc[0] not in LOCALIZACOES_SECRETAS]

    NOME_LOCAL = dict(LOCALIZACAO_CHOICES)
    dispositivos_com_dados = []

    for disp in dispositivos:
        if request.user.user_type in ['batman', 'alfred']:
            estoques_visiveis = disp.estoques.all()
        else:
            estoques_visiveis = [
                est for est in disp.estoques.all()
                if est.localizacao not in LOCALIZACOES_SECRETAS
            ]

        estoques_visiveis = [est for est in estoques_visiveis if est.quantidade > 0]

        estoques_visiveis.sort(
            key=lambda est: (
                est.localizacao in LOCALIZACOES_SECRETAS,
                NOME_LOCAL.get(est.localizacao, est.localizacao).lower()
            )
        )

        total = sum(est.quantidade for est in estoques_visiveis)

        dispositivos_com_dados.append({
            'obj': disp,
            'estoques': estoques_visiveis,
            'total': total,
        })

    return render(request, 'core/lista_dispositivos.html', {
        'dispositivos': dispositivos_com_dados,
        'localizacoes_visiveis': locais_visiveis,
        'tipo_item': 'dispositivo'
    })
