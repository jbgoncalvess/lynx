import json

import paramiko
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.api.models import ContainerLxcList, CurrentCount


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

    print(container_data)
    # Envia os dados como contexto para o template
    return render(request, 'containers/containers.html', {
        'container_data': container_data,
        'ult_reg': ult_reg,
    })


# Função para criar o cliente SSH (Redução de tamanho de código)
def create_client_ssh():
    ip_server = '192.168.2.104'
    user_server = 'lynx'
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_server, username=user_server)
    return client


@login_required
def start_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status != 'RUNNING':
            # Função para criar o cliente SSH
            client = create_client_ssh()
            try:
                command = f"lxc start {container_name}"
                stdin, stdout, stderr = client.exec_command(command)

                # output = stdout.read().decode()
                error = stderr.read().decode()

                # if output:
                #     print(f"Output: {output}")
                if error:
                    print(f"Error: {error}")

                # Somente atualiza o status se não houver erros
                if not error:
                    container.status = 'RUNNING'
                    container.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Container {container_name} iniciado com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao iniciar o container: {error}'
                    })
            finally:
                # Fechar a conexão SSH
                client.close()
        else:
            return JsonResponse({
                'status': 'info',
                'message': f'Container {container_name} já está em execução!'
            })

    except paramiko.SSHException as e:
        return JsonResponse({'status': 'error', 'message': f'Erro de SSH: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})


@login_required
def stop_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status == 'RUNNING':
            # Função para criar o cliente SSH
            client = create_client_ssh()
            try:
                command = f"lxc stop {container_name}"
                stdin, stdout, stderr = client.exec_command(command)

                # output = stdout.read().decode()
                error = stderr.read().decode()

                # if output:
                #     print(f"Output: {output}")
                if error:
                    print(f"Error: {error}")

                # Somente atualiza o status se não houver erros
                if not error:
                    container.status = 'STOPPED'
                    container.save()
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Container {container_name} parado com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao parar o container: {error}'
                    })
            finally:
                # Fechar a conexão SSH
                client.close()
        else:
            return JsonResponse({
                'status': 'info',
                'message': f'Container {container_name} já está parado!'
            })

    except paramiko.SSHException as e:
        return JsonResponse({'status': 'error', 'message': f'Erro de SSH: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})


@login_required
def restart_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status == 'RUNNING':
            # Função para criar o cliente SSH
            client = create_client_ssh()
            try:
                command = f"lxc restart {container_name}"
                stdin, stdout, stderr = client.exec_command(command)
                error = stderr.read().decode()

                if error:
                    print(f"Error: {error}")

                # Somente atualiza o status se não houver erros
                if not error:
                    # Não atualizo o container.status, pois se reiniciou correto ele esta rodando
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Container {container_name} reiniciado com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erro ao reiniciar o container: {error}'
                    })
            finally:
                # Fechar a conexão SSH
                client.close()
        else:
            return JsonResponse({
                'status': 'info',
                'message': f'Container {container_name} está parado, por isso não é possível reiniciá-lo!'
            })

    except paramiko.SSHException as e:
        return JsonResponse({'status': 'error', 'message': f'Erro de SSH: {str(e)}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro inesperado: {str(e)}'})


@csrf_exempt
def swap_ip(request, container_name):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            # print("TESTANDO-swap")
            interface = data.get('interface')
            ip_type = data.get('ip_type').lower()
            ipaddress = data.get('ip_address')

            client = create_client_ssh()
            try:
                # print("TESTANDO-swap-2")
                # Aqui vou ativar o signals do app nginx, assim ele vai remover o container que vai trocar de endereço
                # ipv4 dos containers upstream
                command = (f"lxc config device set {container_name} {interface} {ip_type}.address"
                           f" {ipaddress} && lxc restart {container_name}")
                _, _, stderr = client.exec_command(command)
                error = stderr.read().decode()

                if not error:
                    return JsonResponse({'message': 'Endereço IPv4 trocado com sucesso!'})
                else:
                    return JsonResponse({'error': f'Erro ao adicionar o IPv4: {error}'})

            except paramiko.SSHException as e:
                return JsonResponse({"error": f"Erro de conexão SSH: {str(e)}"}, status=500)
            finally:
                client.close()

        else:
            return JsonResponse({"error": "Método não permitido."}, status=405)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)


@csrf_exempt
def remove_ip(request, container_name):
    try:
        if request.method == 'POST':
            print("TESTANDO-remove")
            data = json.loads(request.body)
            interface = data.get('interface')
            ip_type = data.get('ip_type').lower()
            ipaddress = data.get('ip_address')

            client = create_client_ssh()
            try:
                if ip_type == 'ipv4':
                    pass

                else:
                    pass

                # command = f"lxc config device unset {container_name} {interface} {ip_type}.address"
                # _, _, stderr = client.exec_command(command)
                # error = stderr.read().decode()
                #
                # if not error:
                #     return JsonResponse({'message': 'Endereço IPv4 removido com sucesso!'})
                # else:
                #     return JsonResponse({'error': f'Erro ao remover o IPv4: {error}'})

            except paramiko.SSHException as e:
                return JsonResponse({"error": f"Erro de conexão SSH: {str(e)}"}, status=500)
            finally:
                client.close()

        else:
            return JsonResponse({"error": "Método não permitido."}, status=405)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)
