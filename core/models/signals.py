from django.db.models.signals import post_save
from django.dispatch import receiver
from . import AcaoUsuario, RequisicaoManutencao, SolicitacaoCompra, OrdemCompra, RequisicaoMovimentacao
from core.models.user import CustomUser

@receiver(post_save, sender=RequisicaoManutencao)
def registrar_acao_requisicao_manutencao(sender, instance, created, **kwargs):
    if created:
        AcaoUsuario.objects.create(
            usuario=instance.criado_por,
            acao=f"Enviou requisição de manutenção para {instance.get_item_nome()} (Qtd: {instance.quantidade})"
        )

@receiver(post_save, sender=SolicitacaoCompra)
def registrar_acao_solicitacao_compra(sender, instance, created, **kwargs):
    if created:
        AcaoUsuario.objects.create(
            usuario=instance.criado_por,
            acao=f"Solicitou compra de {instance.nome_item} (Qtd: {instance.quantidade})"
        )

@receiver(post_save, sender=OrdemCompra)
def registrar_acao_ordem_compra(sender, instance, created, **kwargs):
    if created:
        AcaoUsuario.objects.create(
            usuario=instance.criado_por,
            acao=f"Ordem de compra criada para {instance.get_item_nome()} (Qtd: {instance.quantidade})"
        )

@receiver(post_save, sender=RequisicaoMovimentacao)
def registrar_acao_requisicao_movimentacao(sender, instance, created, **kwargs):
    if created:
        AcaoUsuario.objects.create(
            usuario=instance.solicitante,
            acao=f"Solicitou movimentação de {instance.quantidade} {instance.tipo_item} de {instance.origem} para {instance.destino}"
        )
