from apps.api.models import ContainerLxcImage, ContainerLxcList, ContainerMetrics
import re
import paramiko


def create_client_ssh():
    ip_server = '192.168.77.2'
    user_server = 'lynx'
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_server, username=user_server)
    return client


def natural_key(container):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', container.container_name)]


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
        # Verificar se o endereço é válido, pois se meu daemon listar os ips dos containers, em um momento de
        # inicialização, virá sem endereço, ou seja, None
        # print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        # print(first_ipv4)
        if first_ipv4:
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


def check_cpu_usage(cpu_usages):
    # Obter todos os valores de CPU usage que chegaram a view do apps.api, passando por parâmetro
    if cpu_usages:
        # Calcular a média aritmética. Cada container só tem um cpu usage, portanto o número de items cpu_usage
        # é o número dos containers ativos
        total_cpu_usage = sum(cpu_usages)
        num_containers = len(cpu_usages)
        avg_cpu_usage = total_cpu_usage / num_containers

        # Verifica se a média de uso de CPU é igual ou maior que 70%
        if avg_cpu_usage >= 70:
            active_containers()
            containers_running = ContainerLxcList.objects.filter(status='RUNNING')
            update_upstream(containers_running)

        # Se a média for menor, para os containers de aplicação, limitando-se no mínimo 1
        elif avg_cpu_usage <= 20 and num_containers > 1:
            stop_containers()
            containers_running = ContainerLxcList.objects.filter(status='RUNNING')
            update_upstream(containers_running)


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
                container_stopped.status = 'RUNNING'
                container_stopped.save()
                print(f"Container {container_name} iniciado com sucesso!")

        else:
            containers_order_name = sorted(ContainerLxcList.objects.filter(status='RUNNING'), key=natural_key)
            containers = [container.container_name for container in containers_order_name]
            container = containers[-1]
            # print(container)
            new_container_name = ''
            match = re.match(r"([a-zA-Z_-]+)(\d*)$", container)

            if match:
                name = match.group(1)  # Parte das letras
                num = match.group(2)  # Parte numérica
                # print(name)
                # print(num)
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
                # print(f"Última imagem: {image_name}")

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
                    # Aqui eu poderia atualizar forçando a entrada do db e via ssh executando o comando para descobrir
                    # o endereço ip, mas não faço isso, espero a próxima coleta e envio do servidor monitorado
                    # container_stopped.status = 'RUNNING'
                    # container_stopped.save()
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
            container = ContainerMetrics.objects.filter(container_name=containers[-1]).first()
            container.active = False
            container.save()

    except Exception as e:
        print(f"Erro ao conectar via SSH: {str(e)}")

    finally:
        ssh_client.close()
