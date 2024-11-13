from apps.containers.views import create_client_ssh
from apps.api.models import ContainerLxcImage


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


def update_containers():
    # Criar o client SSH
    ssh_client = create_client_ssh()
    # Caminho para o arquivo .yaml local
    local_path = 'static/nginx/containers.yaml'
    # Caminho para o arquivo.yaml do software
    server_path = '/home/lynx/yaml/containers.yaml'
    # última imagem disponível
    image = ContainerLxcImage.objects.order_by('-upload_date').first()
    if image:
        image_name = image.image_name  # Acessa o nome da imagem da última instância
        print(f"Última imagem: {image_name}")
    else:
        print("Nenhuma imagem encontrada.")
        return

    try:
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(local_path, server_path)  # Fazendo upload
        sftp_client.close()

        command = f"lxc launch {image_name} < {server_path}"
        _, _, stderr = ssh_client.exec_command(command)
        error = stderr.read().decode()
        if error:
            print(f"Erro ao executar o comando: {error}")
        else:
            print(f"Container criado com sucesso!")

    except Exception as e:
        print(f"Erro ao conectar via SSH: {str(e)}")
    finally:
        ssh_client.close()
