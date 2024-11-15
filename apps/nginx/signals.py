# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from apps.api.models import ContainerLxcList, ContainerIP, ContainerMetrics
# from apps.nginx.views import update_upstream, active_containers, stop_containers
#
#
# # Recebe qualquer alteração da tabela ContainerLxcList é pai de ContainerIP, então chama container IP automaticamente
# @receiver(pre_save, sender=ContainerLxcList)
# def previous_status(sender, instance, **kwargs):
#     try:
#         # Recupera o container existente do banco de dados e armazena o status do banco para status anterior
#         container = ContainerLxcList.objects.get(pk=instance.pk)
#         instance._status_anterior = container.status
#         # Armazena os IPs v4 que estão atualmente no banco
#         ipv4_addresses = list(
#             ContainerIP.objects.filter(container=container, ip_type='IPv4')
#             .values_list('ip_address', flat=True)
#         )
#         # Adiciona os Ips v4 atuais para v4 anteriores
#         instance._ips_v4_anteriores = ipv4_addresses
#     except ContainerLxcList.DoesNotExist:
#         # Define valores para um container recém-criado
#         instance._status_anterior = None
#         instance._ips_v4_anteriores = []
#
#
# # Atualizar os containers upstream que foram somente ligados e desligados
# # @receiver(post_save, sender=ContainerLxcList)
# # def update_upstream_status(sender, instance, **kwargs):
# #     # Captura os valores anteriores e atuais
# #     status_anterior = getattr(instance, '_status_anterior', None)
# #     status_atual = instance.status
# #
# #     # Se status anterior é diferente do atual, chama update_upstream para atualizar os containers upstream do nginx
# #     if status_anterior != status_atual:
# #         print("UPDATE_UPSTREAM FUNCIONANDO - MUDANÇA DE STATUS")
# #         containers_running = ContainerLxcList.objects.filter(status='RUNNING')
# #         update_upstream(containers_running)
#
#
# # Aqui resolvi com essa gambiarra, pois o relacionamento de ContainerLxcList e ContainerIP é de um para muitos
# # o que significa que sempre que o modelo ContainerLxcList é ativado, o ContainerIP pode ser várias vezes ativado
# @receiver(post_save, sender=ContainerIP)
# def update_upstream_ip(sender, instance, **kwargs):
#     # Obter o container relacionado e capturar os IPs anteriores e atuais
#     container = instance.container
#     ipv4_anteriores = getattr(container, '_ips_v4_anteriores', None)
#     ipv4_atuais = list(
#         ContainerIP.objects.filter(container=container, ip_type='IPv4')
#         .values_list('ip_address', flat=True)
#     )
#
#     print(f"IPv4 ANTERIOR: {ipv4_anteriores} IPv4 ATUAL: {ipv4_atuais}")
#     # Comparar IPs e verificar se a função já foi executada para este evento, pois para cada vez que um endereço é
#     # alterado, pode haver duplicidade. === Procurar melhoria
#     if ipv4_anteriores != ipv4_atuais and not hasattr(container, '_upstream_updated'):
#         print("UPDATE_UPSTREAM FUNCIONANDO - MUDANÇA EM ContainerIP")
#         containers_running = ContainerLxcList.objects.filter(status='RUNNING')
#         update_upstream(containers_running)
#         # Flagzinha para caso ele ja tenha sido executado
#         container._upstream_updated = True


# TESTE 1: Ligar e desligar containers
# TESTE 2: Trocar endereço IPv4
# TESTE 3:
