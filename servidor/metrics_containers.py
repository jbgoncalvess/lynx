import requests
import json
import subprocess
import time

# URL da API onde os dados serão enviados
url = 'http://192.168.2.135:8000/metrics_containers/'  # Substitua pela URL correta da sua API


# Função para converter valores em MiB
def convert_to_mib(value):
    if 'GiB' in value:
        return float(value.replace('GiB', '').strip()) * 1024  # Converte GiB para MiB
    elif 'MiB' in value:
        return float(value.replace('MiB', '').strip())  # Já está em MiB
    elif 'KiB' in value:
        return float(value.replace('KiB', '').strip()) / 1024
    return 0  # Caso não reconheça a unidade


# Função para coletar as métricas de CPU e RAM de cada container ativo
def metrics_collect():
    containers_info = []  # Defina a lista aqui para garantir que exista

    try:
        command = "lxc list --format csv --columns n,u,m,D,s | grep RUNNING | sed 's/,RUNNING//'"
        # Executa o comando para listar os containers ativos e suas métricas de CPU, RAM e disco
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Dividir a saída do comando em linhas
        linhas = result.stdout.strip().split('\n')

        for linha in linhas:
            if linha:  # Ignorar linhas vazias
                # Nome do container, uso de CPU e uso de memória separados por vírgula
                container_name, cpu_usage, ram_usage, disk_usage = linha.split(',')

                # Converter uso de CPU para float (removendo 's')
                cpu_usage = float(cpu_usage.replace('s', '').strip())

                # Converter uso de RAM e disco para MiB
                ram_usage = convert_to_mib(ram_usage)
                disk_usage = convert_to_mib(disk_usage)

                # Criar um dicionário com os dados coletados
                container_data = {
                    'name': container_name,
                    'cpu_usage': cpu_usage,  # Uso de CPU
                    'ram_usage': ram_usage,  # Uso de memória RAM
                    'disk_usage': disk_usage  # Uso do disco
                }

                containers_info.append(container_data)

    except Exception as e:
        print(f"Erro ao coletar métricas dos containers: {e}")

    return containers_info  # Retorne a lista mesmo em caso de erro


# Função para enviar as métricas coletadas para o software
def send_metrics():
    # Coletar as métricas
    metrics_containers = metrics_collect()
    print(metrics_containers)
    # Enviar os dados para o software
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=json.dumps(metrics_containers), headers=headers)
        if response.status_code == 200:
            print("Métricas enviadas com sucesso!")
        else:
            print(f"Erro ao enviar métricas. Status: {response.status_code}, Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")


# Loop infinito para enviar as métricas a cada 30 segundos
while True:
    send_metrics()
    time.sleep(30)  # Aguarda 30 segundos antes de executar novamente
