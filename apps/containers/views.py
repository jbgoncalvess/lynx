from django.shortcuts import render
from apps.api.models import ContainerLxcList, CurrentCount
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import subprocess
import re


def natural_key(container):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', container.container_name)]


@login_required
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


@login_required
def start_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status != 'RUNNING':
            command = f"lxc start {container_name}"
            subprocess.run(command, check=True)

            # Atualiza o 'status' no banco de dados
            container.status = 'RUNNING'
            container.save()

            return JsonResponse({'status': 'success', 'message': f'Container {container_name} iniciado com sucesso!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'Container {container_name} já está em execução!'})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': f'Erro ao iniciar o container {container_name}: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})


@login_required
def stop_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status == 'RUNNING':
            command = f"lxc stop {container_name}"
            subprocess.run(command, check=True)

            # Atualiza o 'status' no banco de dados
            container.status = 'STOPPED'
            container.save()

            return JsonResponse({'status': 'success', 'message': f'Container {container_name} parado com sucesso!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'Container {container_name} já está parado!'})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': f'Erro ao parar o container {container_name}: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})


@login_required
def restart_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status == 'RUNNING':
            command = f"lxc restart {container_name}"
            subprocess.run(command, check=True)

            return JsonResponse({'status': 'success', 'message': f'Container {container_name} reiniciado com sucesso!'})
        else:
            return JsonResponse({'status': 'info', 'message': f'Container {container_name} está parado!'})

    except subprocess.CalledProcessError as e:
        return JsonResponse({'status': 'error', 'message': f'Erro ao reiniciar o container {container_name}: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})
