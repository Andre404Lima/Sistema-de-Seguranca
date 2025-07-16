from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('equipamentos/', views.lista_equipamentos, name='lista_equipamentos'),
    path('dispositivos/', views.lista_dispositivos, name='lista_dispositivos'),
    path('veiculos/', views.lista_veiculos, name='lista_veiculos'),
    path('local/<str:local>/', views.itens_por_local, name='itens_por_local'),
    path('solicitar_movimentacao/', views.solicitar_movimentacao, name='solicitar_movimentacao'),
    path('autorizar-requisicao/<int:req_id>/', views.autorizar_requisicao, name='autorizar_requisicao'),
    path('rejeitar-requisicao/<int:pk>/', views.rejeitar_requisicao, name='rejeitar_requisicao'),
    path('autorizar-solicitacao/<int:solicitacao_id>/', views.autorizar_solicitacao_compra, name='autorizar_solicitacao'),
    path('negar-solicitacao/<int:solicitacao_id>/', views.negar_solicitacao_compra, name='negar_solicitacao'),
    path('solicitar-compra/', views.solicitar_compra, name='solicitar_compra'),
    path('criar-ordem-compra/', views.criar_ordem_compra_direta, name='criar_ordem_compra'),
    path('pagar-ordem/<int:ordem_id>/', views.pagar_ordem_compra, name='pagar_ordem'),
    path('negar-ordem/<int:ordem_id>/', views.negar_ordem_compra, name='negar_ordem'),
    path('manutencao/solicitar/', views.solicitar_manutencao, name='solicitar_manutencao'),
    path('manutencao/aprovar/<int:manutencao_id>/', views.aprovar_envio_manutencao, name='aprovar_envio_manutencao'),
    path('manutencao/negar/<int:manutencao_id>/', views.negar_manutencao, name='negar_manutencao'),
    path('manutencao/concluir/<int:manutencao_id>/', views.concluir_manutencao, name='concluir_manutencao'),
    path('criar/<str:tipo>/', views.criar_item, name='criar_item'),
    path('editar/<str:tipo>/<int:pk>/', views.editar_item, name='editar_item'),
    path('usuarios/', views.controle_usuarios, name='controle_usuarios'),
    path('usuarios/desativar/<int:user_id>/', views.desativar_usuario, name='desativar_usuario'),
    path('usuarios/', views.usuarios_lista, name='usuarios_lista'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
