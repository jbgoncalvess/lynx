from django.shortcuts import render
from apps.api.models import ContainerLxcList, CurrentCount
import re


def natural_key(container):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', container.container_name)]


def containers_view(request):

    ult_reg = CurrentCount.objects.order_by('-time').first()
    # Ordena os containers pelo nome
    containers = sorted(ContainerLxcList.objects.all(), key=natural_key)

    # Inicializa a lista que será passada para o modelo
    container_data = []

    # Itera sobre os containers para coletar os dados
    for container in containers:
        ips_data = []

        # Itera sobre os IPs associados ao container e organiza por tipo de IP e interface
        for ip in container.ips.all():
            ips_data.append({
                'ip_address': ip.ip_address,
                'interface': ip.interface,
                'ip_type': ip.ip_type
            })

        # Adiciona o container e seus respectivos dados (nome, status, IPs) na lista
        container_data.append((container.container_name, container.status, ips_data))

    # Envia os dados como contexto para o template
    return render(request, 'containers/containers.html', {
        'container_data': container_data,
        'ult_reg': ult_reg,
    })

