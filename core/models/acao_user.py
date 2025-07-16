from django.db import models
from .user import CustomUser

class AcaoUsuario(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    acao = models.CharField(max_length=255)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.acao} em {self.data_hora}"