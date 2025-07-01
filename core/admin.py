from django.contrib import admin
from .models.equipamento import Equipamento
from .models.veiculo import Veiculo
from .models.user import CustomUser
from .models.dispositivo import Dispositivo

admin.site.register(Equipamento)
admin.site.register(Veiculo)
admin.site.register(CustomUser)
admin.site.register(Dispositivo)


