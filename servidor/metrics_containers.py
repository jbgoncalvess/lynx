# Neste código eu coleto as métricas que envolvem a máquina host do servidor e não os containers
import requests
import json
import subprocess
import time
from datetime import datetime

# URL da API onde os dados serão enviados
url = 'http://192.168.2.104:8000/metrics_containers/'


# Função para converter valores em MiB
def convert_to_mib(value):
    try:
        if 'GiB' in value:
            return float(value.replace('GiB', '').strip()) * 1024  # Converte GiB para MiB
        elif 'MiB' in value:
            return float(value.replace('MiB', '').strip())  # Já está em MiB
        elif 'KiB' in value:
            return float(value.replace('KiB', '').strip()) / 1024
    except ValueError:
        print(f"Erro: Não foi possível converter '{value}' para MB.")
        return 0


# Função para converter horas para minutos - Possíveis valores example: '12:33' e '57 min'
def convert_to_minutes(value):
    try:
        if ':' in value:
            hour, minute = value.split(':')
            return int(hour) * 60 + int(minute)
        elif ' ' in value:
            minute = value.split(' ')[0]
            return int(minute)
    except ValueError:
        print(f"Erro: Não foi possível converter '{value}' para minutos.")
        return 0


# Função para pegar o último segundo de log, para coletar somente os logs referente aquele segundo
def last_sec(log_file):
    try:
        command = f"tail -n 1 {log_file} | cut -d '[' -f 2 | cut -d ']' -f 1"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            return datetime.strptime(result, '%d/%b/%Y:%H:%M:%S %z')

    except Exception as e:
        print(f"Erro ao enviar a data atual do log: {e}")
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

    requests_count['10.1.1.5'+':80']['upstream_response_times'][0] = 10.0
    requests_count['10.1.1.5'+':80']['upstream_response_times'][1] = 2.0
    requests_count['10.1.1.5'+':80']['upstream_response_times'].append(1.5)

    def average_aritmetica(sublist):
        if sublist:
            return sum(sublist) / len(sublist)
        return 0

    # Para cada IP de container, verifico se ele recebeu uma atribuição de rps
    for container_ip in container_ips:
        # Adiciona o valor de requests_count correspondente ou '0' se não encontrar o IP
        rps.append(str(requests_count.get(container_ip + ":80", {}).get('count', 0)))
        urt.append(str(average_aritmetica(requests_count.get(container_ip + ":80", {}).get('upstream_response_times', 0))))
        rt.append(str(average_aritmetica(requests_count.get(container_ip + ":80", {}).get('request_times', 0))))


    print("TESTANDO\n")
    print(rps)
    print(urt)
    print(rt)
    data = [rps, urt, rt]
    print(data)
    return data


# Função para contar requisições por container no último segundo
def metrics_log(log_file):
    last_timestamp = last_sec(log_file)

    if last_timestamp is None:
        print("Não foi possível obter o timestamp do log.")
        return

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
    print(requests_in_order)
    return requests_in_order


# Função para coletar o valor de uptime de cada container
def get_uptime(container_name):
    # Preciso do 'sed' pois o comando cut é bugado, ele retorna 2 espaçamentos quando é HORA ao invés de MIN
    command = f"lxc exec {container_name} uptime | cut -d ',' -f 1 | cut -d ' ' -f 4,5 | sed 's/^ *//'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print(f"Erro ao obter uptime para {container_name}: {result.stderr}")
        return 0


# Função para coletar as métricas de CPU e RAM de cada container ativo
def metrics_collect():
    log_file = '/var/log/nginx/upstream_access.log'
    containers_info = []  # Defino a lista aqui para garantir que exista
    rps_urt_rt = []
    try:
        command = "lxc list --format csv --columns n,u,m,D,s,N | grep RUNNING | sed 's/,RUNNING//'"
        # Executa o comando para listar os containers ativos e suas métricas de CPU, RAM e disco
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Dividir a saída do comando em linhas
        linhas = result.stdout.strip().split('\n')
        print(linhas)
        # Me retorna o RPS para cada container, em ordem
        rps_urt_rt = metrics_log(log_file)
        print(f'TESTANDOOOOOOOOOOOO: {rps_urt_rt}')
        rps = rps_urt_rt[0]
        urt = rps_urt_rt[1]
        rt = rps_urt_rt[2]
        print(rps)
        print(urt)
        print(rt)
        # Inserir manualmente métricas que não consigo diretamente do lxc list (uptime) e do (rps)
        for n in range(len(linhas)):
            linhas[n] = linhas[n] + ',' + get_uptime(linhas[n].split(',')[0]) + ',' + rps[n] + ',' + urt[n] + ',' + rt[n]

        print(linhas)

        for linha in linhas:
            if linha:  # Ignorar linhas vazias
                # Nome do container, uso de CPU e uso de memória separados por vírgula
                container_name, cpu_usage, ram_usage, disk_usage, processes, uptime, rps, urt, rt = linha.split(',')

                # Converter uso de CPU para float (removendo 's')
                cpu_usage = float(cpu_usage.replace('s', '').strip())

                # Converter uso de RAM e disco para MiB e converter uptime para segundos
                ram_usage = convert_to_mib(ram_usage)
                disk_usage = convert_to_mib(disk_usage)
                processes = int(processes)
                uptime = convert_to_minutes(uptime)
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
                print(container_data)
                containers_info.append(container_data)

    except Exception as e:
        print(f"Erro ao coletar métricas dos containers: {e}")

    return containers_info  # Retorne a lista mesmo em caso de erro


# Função para enviar as métricas coletadas para o software
def send_metrics():
    # Coletar as métricas
    metrics_containers = metrics_collect()
    # print(metrics_containers)
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
    time.sleep(15)  # Aguarda 15 segundos antes de executar novamente
