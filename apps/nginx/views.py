from apps.containers.views import create_client_ssh
from apps.api.models import ContainerLxcImage, ContainerLxcList
from apps.containers.views import natural_key
import re


# Função para atualizar os containers upstream de acordo com seus status
def update_upstream(containers_running):
    # Criar o client SSH
    ssh_client = create_client_ssh()

    # Define o caminho do arquivo de configuração e o tipo de balanceamento de carga
    path_nginx = '/etc/nginx/conf.d/upstream.conf'
    type_balanced = "least_conn;"

    # Inicia a escrita do novo bloco de upstream
    new_upstream = f"upstream containers {{\n  {type_balanced}\n"
    for container in containers_running:
        # Para cada container ativo que está ativo, eu pego seu primeiro endereço IPv4 e adiciono no upstream
        first_ipv4 = container.ips.filter(ip_type='IPv4').values_list('ip_address', flat=True).first()
        new_upstream += f"    server {first_ipv4};\n"
    new_upstream += '}\n'

    command = f"echo '{new_upstream}' > {path_nginx}"

    try:
        # Executa o comando para atualizar o arquivo de configuração via SSH
        _, _, stderr = ssh_client.exec_command(command)
        error = stderr.read().decode()
        if error:
            raise Exception(f"Erro ao atualizar o arquivo upstream: {error}")

        # Recarregar o Nginx (verificar a permissão do usuário lynx e modificar)
        comando_reload_nginx = 'sudo systemctl reload nginx'

        # Executa o comando de recarga do Nginx via SSH
        _, _, stderr = ssh_client.exec_command(comando_reload_nginx)
        error = stderr.read().decode()
        if error:
            raise Exception(f"Erro ao recarregar o Nginx: {error}")

        return True

    except Exception as e:
        print(f"Erro: {str(e)}")
        return False

    finally:
        # Fecha a conexão SSH
        ssh_client.close()


def active_containers():
    # Criar o client SSH
    ssh_client = create_client_ssh()
    # Caminho para o arquivo .yaml local
    local_path = 'static/nginx/containers.yaml'
    # Caminho para o arquivo.yaml do software
    server_path = '/home/lynx/yaml/containers.yaml'

    try:
        # Buscar o primeiro container com status 'STOPPED'
        container_stopped = ContainerLxcList.objects.filter(status='STOPPED').first()

        if container_stopped is not None:
            container_name = container_stopped.container_name
            # Comando para iniciar o container
            command = f"lxc start {container_name}"
            _, _, stderr = ssh_client.exec_command(command)
            error = stderr.read().decode()
            if error:
                print(f"Erro ao executar o comando: {error}")
            else:
                print(f"Container {container_name} iniciado com sucesso!")

        else:
            containers_order_name = sorted(ContainerLxcList.objects.filter(status='RUNNING'), key=natural_key)
            containers = [container.container_name for container in containers_order_name]
            container = containers[-1]
            print(container)
            new_container_name = ''
            match = re.match(r"([a-zA-Z_-]+)(\d*)$", container)

            if match:
                name = match.group(1)  # Parte do prefixo (letras e underscore)
                num = match.group(2)  # Parte numérica (vazia se não houver números)
                print(name)
                print(num)
                if num:  # Se tem uma parte numérica
                    num = int(num)
                    new_num = num + 1
                    new_container_name = f"{name}{new_num}"
                else:
                    new_container_name = f"{container}1"

            # Última imagem disponível
            image = ContainerLxcImage.objects.order_by('-upload_date').first()
            if image:
                image_name = image.image_name  # Acessa o nome da imagem da última instância
                print(f"Última imagem: {image_name}")

                # Fazer upload do arquivo .yaml
                sftp_client = ssh_client.open_sftp()
                sftp_client.put(local_path, server_path)  # Fazendo upload
                sftp_client.close()

                # Comando para criar o novo container com a imagem
                command = f"lxc launch {image_name} {new_container_name} < {server_path}"
                _, _, stderr = ssh_client.exec_command(command)
                error = stderr.read().decode()
                if error:
                    print(f"Erro ao executar o comando: {error}")
                else:
                    print(f"Container {new_container_name} criado com sucesso!")
            else:
                print("Nenhuma imagem encontrada.")
                return

    except Exception as e:
        print(f"Erro ao conectar via SSH: {str(e)}")

    finally:
        # Fechar a conexão SSH independentemente de ocorrer erro ou não
        ssh_client.close()


def stop_containers():
    # Criar o client SSH
    ssh_client = create_client_ssh()

    try:
        containers_order_name = sorted(ContainerLxcList.objects.filter(status='RUNNING'), key=natural_key)
        containers = [container.container_name for container in containers_order_name]
        command = f"lxc stop {containers[-1]}"
        _, _, stderr = ssh_client.exec_command(command)
        error = stderr.read().decode()
        if error:
            print(f"Erro ao executar o comando: {error}")
        else:
            print(f"Container {containers[-1]} parado com sucesso!")
            container = ContainerLxcList.objects.filter(container_name=containers[-1]).first()
            container.status = 'STOPPED'
            container.save()

    except Exception as e:
        print(f"Erro ao conectar via SSH: {str(e)}")

    finally:
        ssh_client.close()
