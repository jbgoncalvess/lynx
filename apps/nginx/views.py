from apps.containers.views import create_client_ssh


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
        stdin, stdout, stderr = ssh_client.exec_command(command)
        error_output = stderr.read().decode()
        if error_output:
            raise Exception(f"Erro ao atualizar o arquivo upstream: {error_output}")

        # Recarregar o Nginx (verificar a permissão do usuário lynx e modificar )
        comando_reload_nginx = 'sudo systemctl reload nginx'

        # Executa o comando de recarga do Nginx via SSH
        stdin, stdout, stderr = ssh_client.exec_command(comando_reload_nginx)
        error_output = stderr.read().decode()
        if error_output:
            raise Exception(f"Erro ao recarregar o Nginx: {error_output}")

        return True

    except Exception as e:
        print(f"Erro: {str(e)}")
        return False

    finally:
        # Fecha a conexão SSH
        ssh_client.close()
