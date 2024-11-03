import os.path
import requests
import json
import subprocess
import time
from datetime import datetime

# URL da API onde os dados serão enviados
url = 'http://192.168.77.1:8000/metrics_containers/'


# Função para pegar o último segundo de log, para coletar somente os logs referente aquele segundo
def last_sec(log_file):
    try:
        command = f"tail -n 1 {log_file} | cut -d '[' -f 2 | cut -d ']' -f 1"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            print(datetime.strptime(result, '%d/%b/%Y:%H:%M:%S %z'))
            return datetime.strptime(result, '%d/%b/%Y:%H:%M:%S %z')

    except Exception as e:
        print(f"Erro ao enviar a data atual do log.")
        return None


def resolv_ip_name(requests_count):
    # Comando para listar os containers LXC que estão rodando e pegar o IP (ordenado por nome de container)
    command = ("lxc list --format csv --columns n,4,s | grep RUNNING | cut -d ' ' -f 1 | sed 's/,RUNNING//' | cut -d "
               "',' -f 2")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    # Separo a saída do comando quebrando a linha, isso faz com que eu crie uma lista
    container_ips = result.stdout.strip().split('\n')

    # Inicializa uma lista para armazenar as contagens de RPS, upstream_response_times e request_times por container
    rps = []
    urt = []
    rt = []

    def average_aritmetica(sublist):
        if sublist:
            return sum(sublist) / len(sublist)
        return 0

    # Para cada IP de container, verifico se ele recebeu uma atribuição de rps
    for container_ip in container_ips:
        # Adiciona o valor de requests_count correspondente ou '0' se não encontrar o IP
        rps.append(str(requests_count.get(container_ip + ":80", {}).get('count', 0)))
        urt.append(
            str(average_aritmetica(requests_count.get(container_ip + ":80", {}).get('upstream_response_times', 0))))
        rt.append(str(average_aritmetica(requests_count.get(container_ip + ":80", {}).get('request_times', 0))))

    data = [rps, urt, rt]
    return data


# Função para contar requisições por container no último segundo
def metrics_log(log_file):
    # Verificar se existe o arquivo e ele não está vazio devido à rotina do rotate
    if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
        last_timestamp = last_sec(log_file)

    else:
        print("Arquivo de log não existe ou não tem logs devido ao rotate.")
        return None

    # Contador de requisições
    requests_count = {}
    # O último segundo
    target_timestamp = last_timestamp

    with open(log_file, 'r') as f:
        for line in f:
            # Pega o timestamp da linha
            timestamp_str = line.split('[')[1].split(']')[0].strip()
            # print(timestamp_str)
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            # Se a linha está dentro do último segundo, conta a requisição
            if timestamp == target_timestamp:
                # Captura o IP upstream
                upstream_ip = line.split('upstream: ')[1].split(',')[0].strip()
                # print(upstream_ip)
                upstream_response_time = float(line.split('upstream_response_time: ')[1].split(',')[0].strip())
                request_time = float(line.split('request_time: ')[1].split(',')[0].strip())
                # print(upstream_response_time, request_time)
                # Incrementa o contador para esse IP e adiciona os tempos, já que pode ser mais 1 por sec
                if upstream_ip in requests_count:
                    requests_count[upstream_ip]['count'] += 1
                    requests_count[upstream_ip]['upstream_response_times'].append(upstream_response_time)
                    requests_count[upstream_ip]['request_times'].append(request_time)
                else:
                    # requests_count[upstream_ip] = 1
                    requests_count[upstream_ip] = {
                        'count': 1,
                        'upstream_response_times': [upstream_response_time],
                        'request_times': [request_time]
                    }

    requests_in_order = resolv_ip_name(requests_count)
    return requests_in_order


# Função para coletar o uso de CPU de um container
def get_cpu_usage(container_name):
    try:
        # Comando para coletar o uso de CPU somando o uso do usuário ($2), sistema ($4) e processos ajustados ($6)
        command = f"lxc exec {container_name} -- top -bn1 | grep '%Cpu(s)' | awk '{{print $2 + $4 + $6}}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            return result.strip('%')
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
            return result.strip('%')
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
                return str(int(hour) * 60 + int(minute))
            else:
                return result
        else:
            print(f"Erro ao obter uptime para {container_name}: {result.stderr}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando para uptime: {e}")
        return None


# Função para coletar as métricas de CPU e RAM de cada container ativo
def metrics_collect():
    log_file = '/var/log/nginx/upstream_access.log'
    containers_info = []  # Defino a lista aqui para garantir que exista
    rps_urt_rt = []
    try:
        # Name,
        command = "lxc list --format csv --columns n,M,s,N | grep RUNNING | sed 's/,RUNNING//' | sed 's/%//g'"
        # Executa o comando para listar os containers ativos e suas métricas de CPU, RAM e disco
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Dividir a saída do comando em linhas
        linhas = result.stdout.strip().split('\n')
        # Me retorna o RPS para cada container, em ordem
        rps_urt_rt = metrics_log(log_file)
        if rps_urt_rt is None:
            # Se o arquivo de log está vazio (rotate aconteceu no momento ou ninguém ta acessando o servidor mesmo,
            # eu adiciono 0 que indica que sem métricas de rps, urt rt)
            rps = '0'
            urt = '0'
            rt = '0'
            # Inserir manualmente métricas que não consigo diretamente do lxc list (uptime) e do (rps)
            for n in range(len(linhas)):
                container_name = linhas[n].split(',')[0]
                linhas[n] = (linhas[n] + ',' + get_cpu_usage(container_name) + ',' + get_disk_usage(container_name)
                             + ',' + get_uptime(container_name) + ',' + rps + ',' + urt + ',' + rt)
        else:
            rps = rps_urt_rt[0]
            urt = rps_urt_rt[1]
            rt = rps_urt_rt[2]
            # Mesma inserção manual
            for n in range(len(linhas)):
                container_name = linhas[n].split(',')[0]
                linhas[n] = (linhas[n] + ',' + get_cpu_usage(container_name) + ',' + get_disk_usage(container_name)
                             + ',' + get_uptime(container_name) + ',' + rps[n] + ',' + urt[n] + ',' + rt[n])

        for linha in linhas:
            if linha:  # Ignorar linhas vazias
                # Nome do container, uso de CPU e uso de memória separados por vírgula
                container_name, ram_usage, processes, cpu_usage, disk_usage, uptime, rps, urt, rt = linha.split(',')

                # Converter uso de RAM e disco para MiB e converter uptime para segundos
                ram_usage = float(ram_usage)
                processes = int(processes)
                cpu_usage = float(cpu_usage)
                disk_usage = float(disk_usage)
                uptime = int(uptime)
                rps = int(rps)
                urt = float(urt)
                rt = float(rt)
                # Criar um dicionário com os dados coletados
                container_data = {
                    'name': container_name,
                    'cpu_usage': cpu_usage,  # Uso de CPU
                    'ram_usage': ram_usage,  # Uso de memória RAM
                    'disk_usage': disk_usage,  # Uso do disco
                    'uptime': uptime,  # Tempo ativo do container
                    'processes': processes,
                    'rps': rps,
                    'urt': urt,
                    'rt': rt
                }
                containers_info.append(container_data)

    except Exception as e:
        print(f"Erro ao coletar métricas dos containers: {e}")

    return containers_info  # Retorne a lista mesmo em caso de erro


# Função para enviar as métricas coletadas para o software
def send_metrics():
    # Coletar as métricas
    metrics_containers = metrics_collect()

    # Formatar os dados para debug, já que várias vezes eu enviei dados errados para o back
    print("Dados dos Containers:")
    for container in metrics_containers:
        print(f"Container: {container['name']:<3}| "
              f"CPU Usage: {container['cpu_usage']:<4}%| "
              f"RAM Usage: {container['ram_usage']:<4}%| "
              f"Disk Usage: {container['disk_usage']:<4}%| "
              f"Uptime: {container['uptime']:<4}min| "
              f"Processes: {container['processes']:<3}| "
              f"RPS: {container['rps']:<2}rps| "
              f"URT: {container['urt']:<4}s| "
              f"RT: {container['rt']:<4}s")

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


while True:
    send_metrics()
    time.sleep(15)
