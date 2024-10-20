from apps.api.models import ContainerLxcList

import paramiko
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.api.models import ContainerLxcList


#
# def buscar_status(container_name = "c1"):
#     try:
#         container = ContainerLxcList.objects.get(container_name=container_name)
#         print(container.status)
#     except ContainerLxcList.DoesNotExist:
#         return None

# buscar_status()

def start_container(container_name="c1"):
    try:
        # Configurações para a conexão SSH
        remote_ip = '192.168.2.110'  # Endereço IP da máquina remota
        ssh_username = 'lynx'  # Nome de usuário SSH - Criar no servidor um usuário para o software
        # ssh_key_path = '/caminho/para/sua/chave_privada'  # Caminho para a chave privada

        # Cria um cliente SSH
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(remote_ip, username=ssh_username)

        # Comando a ser executado na máquina remota
        command = f"lxc info {container_name}"

        # Executa o comando
        stdin, stdout, stderr = client.exec_command(command)

        # Lê a saída e o erro do comando
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")

    except Exception as e:
        pass


start_container()
