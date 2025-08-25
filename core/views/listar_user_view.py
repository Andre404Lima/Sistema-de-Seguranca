from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import CustomUser

class ListaUsuarioView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'usuarios_lista.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return CustomUser.objects.filter(is_active=True)