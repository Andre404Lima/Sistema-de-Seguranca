from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('itens/<str:categoria>/', views.ItensPorCategoriaView.as_view(), name='itens_categoria'),
    path('local/<str:local>/', views.ItensPorLocalView.as_view(), name='itens_por_local'),
    path('solicitar_movimentacao/', views.SolicitarMovimentacaoView.as_view(), name='solicitar_movimentacao'),
    path('autorizar-requisicao/<int:req_id>/', views.AutorizarRequisicaoView.as_view(), name='autorizar_requisicao'),
    path('rejeitar-requisicao/<int:pk>/', views.RejeitarRequisicaoView.as_view(), name='rejeitar_requisicao'),
    path('autorizar-solicitacao/<int:solicitacao_id>/', views.AutorizarSolicitacaoCompraView.as_view(), name='autorizar_solicitacao'),
    path('negar-solicitacao/<int:solicitacao_id>/', views.NegarManutencaoView.as_view, name='negar_solicitacao'),
    path('solicitar-compra/', views.SolicitarCompraView.as_view(), name='solicitar_compra'),
    path('criar-ordem-compra/', views.CriarOrdemCompraDiretaView.as_view(), name='criar_ordem_compra'),
    path('pagar-ordem/<int:ordem_id>/', views.PagarOrdemCompraView.as_view(), name='pagar_ordem'),
    path('negar-ordem/<int:ordem_id>/', views.NegarOrdemCompraView.as_view, name='negar_ordem'),
    path('manutencao/solicitar/', views.SolicitarManutencaoView.as_view(), name='solicitar_manutencao'),
    path('manutencao/aprovar/<int:manutencao_id>/', views.AprovarManutencaoView.as_view(), name='aprovar_envio_manutencao'),
    path('manutencao/negar/<int:manutencao_id>/', views.NegarManutencaoView.as_view(), name='negar_manutencao'),
    path('manutencao/concluir/<int:manutencao_id>/', views.ConcluirManutencaoView.as_view(), name='concluir_manutencao'),
    path('criar/<str:tipo>/', views.CriarItemView.as_view(), name='criar_item'),
    path('editar/<str:tipo>/<int:pk>/', views.EditarItemView.as_view(), name='editar_item'),
    path('controle-usuarios/', views.ControleUsuariosView.as_view(), name='controle_usuarios'),
    path('controle-usuarios/desativar/<int:user_id>/', views.ControleUsuariosView.as_view(), name='desativar_usuario'),
    path('usuarios/', views.ListaUsuarioView.as_view(), name='usuarios_lista'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
