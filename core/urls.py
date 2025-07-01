from django.urls import path
from . import views
from .views import lista_equipamentos, lista_dispositivos, lista_veiculos

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('equipamentos/', lista_equipamentos, name='lista_equipamentos'),
    path('dispositivos/', lista_dispositivos, name='lista_dispositivos'),
    path('veiculos/', lista_veiculos, name='lista_veiculos'),
]

