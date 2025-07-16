from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from core.models import CustomUser

@login_required
@require_POST
def desativar_usuario(request, user_id):
    current_user = request.user
    current_type = current_user.user_type

    if current_type not in ['administrador', 'batman', 'alfred']:
        return HttpResponseForbidden("Você não tem permissão para desativar usuários.")

    usuario = get_object_or_404(CustomUser, pk=user_id)

    if current_type == 'administrador' and usuario.user_type in ['batman', 'alfred']:
        return HttpResponseForbidden("Administrador não pode desativar usuários Batman ou Alfred.")

    if usuario == current_user:
        return HttpResponseForbidden("Você não pode desativar seu próprio usuário.")

    usuario.is_active = False
    usuario.save()

    return redirect('controle_usuarios')
