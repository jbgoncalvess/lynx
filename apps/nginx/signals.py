from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.api.models import ContainerLxcList
from apps.nginx.views import update_upstream


# Quando o status de ContainerLxcList for alterado, o modelo vai me mandar um sinal
# Antes de alterar o modelo eu salvo o valor que tinha lá em instance._status_anterior
# Se o valor não existe, significa que o container foi criado agora, portanto status anterior é None
@receiver(pre_save, sender=ContainerLxcList)
def capturar_status_anterior(sender, instance, **kwargs):
    print("PRE_SAVE!")
    try:
        container = ContainerLxcList.objects.get(pk=instance.pk)
        instance._status_anterior = container.status
    except ContainerLxcList.DoesNotExist:
        instance._status_anterior = None


# Aqui eu salvo o novo valor que foi inserido e comparo com o anterior
# Se eles forem diferentes, logo chama a função para atualizar os containers upstream
# Nota-se que se o container for iniciado agora, o status anterior é none, que obviamente será diferente do atual
@receiver(post_save, sender=ContainerLxcList)
def atualizar_arquivo_nginx(sender, instance, **kwargs):
    print("POST_SAVE!")
    status_anterior = getattr(instance, '_status_anterior', None)
    status_atual = instance.status

    if status_anterior != status_atual:
        print('Teste')
        containers_rodando = ContainerLxcList.objects.filter(status='RUNNING')
        update_upstream(containers_rodando)
