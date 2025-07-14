from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('equipamentos/', views.lista_equipamentos, name='lista_equipamentos'),
    path('dispositivos/', views.lista_dispositivos, name='lista_dispositivos'),
    path('veiculos/', views.lista_veiculos, name='lista_veiculos'),
    path('local/<str:local>/', views.itens_por_local, name='itens_por_local'),
    path('solicitar_movimentacao/', views.solicitar_movimentacao, name='solicitar_movimentacao'),
    path('autorizar-requisicao/<int:req_id>/', views.autorizar_requisicao, name='autorizar_requisicao'),
    path('rejeitar-requisicao/<int:req_id>/', views.rejeitar_requisicao, name='rejeitar_requisicao'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


