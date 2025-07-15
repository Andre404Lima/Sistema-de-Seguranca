from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models.dispositivo import EstoqueDispositivo
from core.models.equipamento import EstoqueEquipamento
from core.models.veiculo import EstoqueVeiculo
from core.constants import LOCALIZACAO_CHOICES

@login_required
def itens_por_local(request, local):
    locais_secretos = [cod for cod, _ in LOCALIZACAO_CHOICES[7:]]
    nome_local = dict(LOCALIZACAO_CHOICES).get(local, local)
    user_type = request.user.user_type

    localizacoes_visiveis = LOCALIZACAO_CHOICES if user_type in ['batman', 'alfred'] else [
        loc for loc in LOCALIZACAO_CHOICES if loc[0] not in locais_secretos
    ]

    if local in locais_secretos and user_type not in ['batman', 'alfred']:
        return render(request, 'core/itens_por_local.html', {
            'local': nome_local,
            'dispositivos_estoque': [],
            'equipamentos_estoque': [],
            'veiculos_estoque': [],
            'localizacoes_visiveis': localizacoes_visiveis,
        })

    def filtro(model, fk_field):
        qs = model.objects.filter(localizacao=local, quantidade__gt=0).select_related(fk_field)
        if user_type not in ['batman', 'alfred']:
            qs = qs.exclude(**{f"{fk_field}__secret": True})
        qs = qs.order_by(f"{fk_field}__secret", f"{fk_field}__nome" if fk_field != "veiculo" else f"{fk_field}__modelo")
        return qs

    return render(request, 'core/itens_por_local.html', {
        'local': nome_local,
        'dispositivos_estoque': filtro(EstoqueDispositivo, 'dispositivo'),
        'equipamentos_estoque': filtro(EstoqueEquipamento, 'equipamento'),
        'veiculos_estoque': filtro(EstoqueVeiculo, 'veiculo'),
        'localizacoes_visiveis': localizacoes_visiveis,
    })
