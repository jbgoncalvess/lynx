import json
import re
import paramiko
import time
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render
from apps.api.models import ContainerLxcList, HostContainersConnections, ContainerIP
from apps.nginx.views import update_upstream


def natural_key(container):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', container.container_name)]


@login_required
def containers_view(request):
    ult_reg = HostContainersConnections.objects.order_by('-time').first()
    print(ult_reg)
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
    ip_server = '192.168.77.2'
    user_server = 'lynx'
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_server, username=user_server)
    return client


@login_required
@require_http_methods(["POST"])
def start_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status != 'RUNNING':
            # Função para criar o cliente SSH
            client = create_client_ssh()
            try:
                command = f"lxc start {container_name}"
                _, _, stderr = client.exec_command(command)
                error = stderr.read().decode()

                if error:
                    print(f"Error: {error}")

                # Somente atualiza o status se não houver erros
                if not error:
                    command = f'lxc list {container_name} --format csv -c 4 | awk \'{{print $1}}\''
                    _, stdout, stderr = client.exec_command(command)
                    error = stderr.read().decode()
                    ipaddress = stdout.read().decode().strip()
                    while ipaddress == '':
                        print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                        _, stdout, stderr = client.exec_command(command)
                        ipaddress = stdout.read().decode().strip()
                        if error:
                            break
                            time.sleep(3)

                    print(
                        f"=================================================================================================")
                    print(
                        f"=================================================================================================")
                    print(ipaddress)
                    print(error)
                    print(
                        f"=================================================================================================")
                    print(
                        f"=================================================================================================")
                    if not error and ipaddress:
                        container.status = 'RUNNING'
                        container.save()
                        ipv4, created = ContainerIP.objects.get_or_create(container=container, ip_type='IPv4')
                        ipv4.ip_address = ipaddress
                        ipv4.save()
                        # Chamo a função para atualizar o arquivo upstream do nginx
                        containers_running = ContainerLxcList.objects.filter(status='RUNNING')
                        update_upstream(containers_running)
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
@require_http_methods(["POST"])
def stop_container(request, container_name):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        if container.status == 'RUNNING':
            # Função para criar o cliente SSH
            client = create_client_ssh()
            try:
                command = f"lxc stop {container_name}"
                _, _, stderr = client.exec_command(command)

                error = stderr.read().decode()

                if error:
                    print(f"Error: {error}")

                if not error:
                    container.status = 'STOPPED'
                    container.save()
                    containers_running = ContainerLxcList.objects.filter(status='RUNNING')
                    update_upstream(containers_running)
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
@require_http_methods(["POST"])
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


@login_required
@require_http_methods(["PUT"])
def swap_ip(request, container_name):
    try:
        data = json.loads(request.body)
        interface = data.get('interface')
        ipaddress = data.get('ip_address')

        client = create_client_ssh()
        try:
            # print("TESTANDO-swap-2")
            # Aqui vou ativar o signals do app nginx, assim ele vai remover o container que vai trocar de endereço
            # ipv4 dos containers upstream
            command = (f"lxc config device set {container_name} {interface} ipv4.address"
                       f" {ipaddress} && lxc restart {container_name}")
            _, _, stderr = client.exec_command(command)
            error = stderr.read().decode()

            if not error:
                container = ContainerLxcList.objects.get(container_name=container_name)
                ipv4 = ContainerIP.objects.filter(container=container, ip_type='IPv4').first()
                ipv4.ip_address = ipaddress
                ipv4.save()
                # Após buscar a instância do endereço IP, eu atualizo chamando update_upstream, que vai adicionar o novo
                # endereço
                containers_running = ContainerLxcList.objects.filter(status='RUNNING')
                update_upstream(containers_running)
                return JsonResponse({'message': 'Endereço IPv4 trocado com sucesso!'})
            else:
                return JsonResponse({'error': f'Erro ao adicionar o IPv4: {error}'})

        except paramiko.SSHException as e:
            return JsonResponse({"error": f"Erro de conexão SSH: {str(e)}"}, status=500)
        finally:
            client.close()

    except json.JSONDecodeError:
        return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)


@login_required
@require_http_methods(["PATCH"])
def toggle_ipv6(request, container_name):
    try:
        data = json.loads(request.body)
        action_ipv6 = data.get('action')  # 'enable' ou 'disable'

        client = create_client_ssh()  # Função que cria uma conexão SSH
        try:
            # Definindo o caminho do arquivo
            file_path = "/etc/netplan/50-cloud-init.yaml"

            if action_ipv6 == 'desativado':
                command = (
                    f"lxc exec {container_name} -- /bin/bash -c \""
                    f"sed -i '/accept-ra:/d; /dhcp4: true/ a\\"
                    f"            accept-ra: false' {file_path}\""
                )

            elif action_ipv6 == 'ativado':
                command = (
                    f"lxc exec {container_name} -- /bin/bash -c \""
                    f"sed -i '/accept-ra:/d; /dhcp4: true/ a\\"
                    f"            accept-ra: true' {file_path}\""
                )

            else:
                return JsonResponse({"error": "Ação inválida."}, status=400)

            # Executando o comando SSH
            _, _, stderr = client.exec_command(command)
            error = stderr.read().decode()

            if not error:
                # Me forcei a usar o sleep, pois não sei porque não ta dando para usar o netplan apply.
                # Tem algo haver com ser container e não gerenciar tudo, em vez disso, restarto
                time.sleep(7.7)
                command_restart = f"lxc restart {container_name}"
                _, _, stderr_apply = client.exec_command(command_restart)
                error_apply = stderr_apply.read().decode()

                if not error_apply:
                    return JsonResponse({'message': f'IPv6 {action_ipv6} com sucesso!'})
                else:
                    return JsonResponse({'error': f'Erro ao aplicar mudanças no netplan: {error_apply}'})

            else:
                return JsonResponse({'error': f'Erro ao alterar IPv6: {error}'})

        except paramiko.SSHException as e:
            return JsonResponse({"error": f"Erro de conexão SSH: {str(e)}"}, status=500)
        finally:
            client.close()

    except json.JSONDecodeError:
        return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)
