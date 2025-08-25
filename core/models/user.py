from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('funcionario', 'Funcionário'),
        ('gerente', 'Gerente'),
        ('administrador', 'Administrador'),
        ('batman', 'Batman'),
        ('alfred','Alfred')
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='funcionario')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


    def get_permissoes(self):
        #Retorna: pode_criar, pode_desativar, tipos_permitidos, usuarios_queryset, base_qs
        #baseado no tipo do usuário.
        from core.models.acao_user import AcaoUsuario
        from core.models.user import CustomUser

        pode_criar = False
        pode_desativar = False
        tipos = []
        usuarios = CustomUser.objects.none()
        base_qs = AcaoUsuario.objects.none()

        if self.user_type == 'funcionario':
            base_qs = AcaoUsuario.objects.filter(usuario__user_type='funcionario')

        elif self.user_type == 'gerente':
            base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=['funcionario', 'gerente'])
            usuarios = CustomUser.objects.filter(user_type__in=['funcionario', 'gerente'], is_active=True)

        elif self.user_type == 'administrador':
            tipos = ['funcionario', 'gerente', 'administrador']
            base_qs = AcaoUsuario.objects.filter(usuario__user_type__in=tipos)
            usuarios = CustomUser.objects.filter(user_type__in=tipos, is_active=True)
            pode_criar = True
            pode_desativar = True

        elif self.user_type in ['batman', 'alfred']:
            tipos = ['funcionario', 'gerente', 'administrador', 'batman', 'alfred']
            base_qs = AcaoUsuario.objects.all()
            usuarios = CustomUser.objects.filter(is_active=True)
            pode_criar = self.user_type == 'batman'
            pode_desativar = self.user_type == 'batman'

        return pode_criar, pode_desativar, tipos, usuarios, base_qs