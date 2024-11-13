# import paramiko
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from apps.api.models import ContainerLxcList
#
# container = ContainerLxcList.objects.get()

from apps.nginx.views import active_containers

try:
    active_containers()
except Exception as e:
    print(f"Ocorreu um erro: {str(e)}")
