import requests
import json
import subprocess
import time

# URL da API onde os dados serão enviados
url = 'http://192.168.77.1:8000/api/metrics_containers/'


def contar_containers_ativos():
    try:
        command = "lxc list --format csv --columns s | grep -c RUNNING"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        active_count = int(result.stdout.strip())
        print(f"Número de containers ativos: {active_count}")
        return active_count
    except Exception as e:
        print(f"Erro ao contar containers: {e}")
        return 0


# Função para coletar o uso de CPU de um container
def get_cpu_usage(container_name):
    try:
        # Comando para coletar o uso de CPU somando o uso do usuário ($2), sistema ($4) e processos ajustados ($6)
        command = f"lxc exec {container_name} -- top -bn1 | grep '%Cpu(s)' | awk '{{print $2 + $4 + $6}}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            return float(result.strip('%'))
        else:
            print(f"Erro ao obter uso de CPU para {container_name}: {result.stderr}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando para uso de CPU: {e}")
        return None


# Função para coletar o uso do disco em um container
def get_disk_usage(container_name):
    try:
        # Comando para coletar o uso de disco no sistema de arquivos root '/'
        command = f"lxc exec {container_name} -- df -h / | awk 'NR==2 {{print $5}}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            return float(result.strip('%'))
        else:
            print(f"Erro ao obter uso de disco para {container_name}: {result.stderr}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando para uso de disco: {e}")
        return None


# Função para coletar o uptime de um container
def get_uptime(container_name):
    try:
        # Usei o 'awk' para extrair apenas o tempo de uptime
        command = f"lxc exec {container_name} -- uptime | awk '{{print $3}}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            result = result.strip(',')
            # Converter hora em minutos para padronizar os dados
            if ':' in result:
                hour, minute = result.split(':')
                return float(int(hour) * 60 + int(minute))
            else:
                return float(result)
        else:
            print(f"Erro ao obter uptime para {container_name}: {result.stderr}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando para uptime: {e}")
        return None


def get_active_connections():
    # Usa curl para acessar o endpoint do stub_status
    try:
        command = "curl -s http://localhost/nginx_status | grep 'Active connections:' | awk '{print $3}'"
        result = subprocess.check_output(command, shell=True)
        active_connections = result.decode('utf-8').strip()
        return int(active_connections)

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando curl: {e}")
        return None

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None


def get_requests(container_name=None):
    try:
        command = "curl -s http://localhost/nginx_status | awk 'NR==3 {print $3}'"
        if container_name is None:
            # Comando para a máquina host (balanceador de carga)
            result = subprocess.check_output(command, shell=True)
        else:
            # Comando para o container em questão
            command = f"lxc exec {container_name} -- {command}"
            result = subprocess.check_output(command, shell=True)

        request = result.decode('utf-8').strip()
        return int(request)

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando curl: {e}")
        return None

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None


# Função para coletar as métricas de CPU e RAM de cada container ativo
def metrics_collect():
    containers_info = []  # Defino a lista aqui para garantir que exista
    try:
        # Name,
        command = "lxc list --format csv --columns n,M,s,N | grep RUNNING | sed 's/,RUNNING//' | sed 's/%//g'"
        # Executa o comando para listar os containers ativos e suas métricas de CPU, RAM e disco
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Dividir a saída do comando em linhas
        linhas = result.stdout.strip().split('\n')

        for linha in linhas:
            if linha:
                # Nome do container, uso de CPU e uso de memória separados por vírgula
                container_name, ram_usage, processes = linha.split(',')
                ram_usage = float(ram_usage)
                processes = int(processes)
                cpu_usage = get_cpu_usage(container_name)
                disk_usage = get_disk_usage(container_name)
                uptime = get_uptime(container_name)
                request_c = get_requests(container_name)

                # Criar um dicionário com os dados coletados
                container_data = {
                    'name': container_name,
                    'cpu_usage': cpu_usage,  # Uso de CPU
                    'ram_usage': ram_usage,  # Uso de memória RAM
                    'disk_usage': disk_usage,  # Uso do disco
                    'uptime': uptime,  # Tempo ativo do container
                    'processes': processes,
                    'request_c': request_c
                }
                containers_info.append(container_data)

    except Exception as e:
        print(f"Erro ao coletar métricas dos containers: {e}")

    return containers_info  # Retorne a lista mesmo em caso de erro


# Função para enviar as métricas coletadas para o software
def send_metrics():
    # Coletar as métricas
    metrics_containers = metrics_collect()
    active_containers = contar_containers_ativos()
    active_connections = get_active_connections()
    request = get_requests()

    data = {
        'active_containers': active_containers,
        'active_connections': active_connections,
        'requests': request,
        'metrics_containers': metrics_containers
    }
    print("Dados do servidor host (balanceador):")
    print(f"active_containers: {active_containers}| active_connections: {active_connections}| requests: {request}")

    # Formatar os dados para debug, já que várias vezes eu enviei dados errados para o back
    print("Dados dos Containers:")
    for container in metrics_containers:
        print(f"Container: {container['name']:<3}| "
              f"CPU Usage: {container['cpu_usage']:<4}%| "
              f"RAM Usage: {container['ram_usage']:<4}%| "
              f"Disk Usage: {container['disk_usage']:<4}%| "
              f"Uptime: {container['uptime']:<4}min| "
              f"Processes: {container['processes']:<3}| "
              f"Request_Containers: {container['request_c']:<3}| "
              )

    # Enviar os dados para o software
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token f8a024c16665a99d561940c16712ea349351c3a6302650f2b3175b98282c30e9'
    }
    exit(0)
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("Métricas enviadas com sucesso!")
        else:
            print(f"Erro ao enviar métricas. Status: {response.status_code}, Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")


while True:
    send_metrics()
    time.sleep(15)
