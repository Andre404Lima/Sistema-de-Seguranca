from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import CustomUser

@login_required
def usuarios_lista(request):
    usuarios = CustomUser.objects.filter(is_active=True)
    return render(request, 'usuarios_lista.html', {'usuarios': usuarios})