from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.api.models import ContainerLxcList, ContainerIP
from .views import update_upstream

# Variável global para armazenar o status anterior
status_anterior = None


@receiver(pre_save, sender=ContainerLxcList)
def capturar_status_anterior(sender, instance, **kwargs):
    global status_anterior
    print("ENTROU AQUI 1")
    try:
        container = ContainerLxcList.objects.get(pk=instance.pk)
        status_anterior = container.status
    except ContainerLxcList.DoesNotExist:
        # Se o container não existir, é um novo registro
        status_anterior = None


@receiver(post_save, sender=ContainerLxcList)
def atualizar_arquivo_nginx(sender, instance, **kwargs):
    global status_anterior
    status_atual = instance.status
    print("ENTROU AQUI 2")

    # Verifica se houve alteração no status do container
    if status_anterior != status_atual:
        # Se o status mudou, atualize o arquivo de upstream
        containers_rodando = ContainerLxcList.objects.filter(status='RUNNING')
        update_upstream(containers_rodando)
