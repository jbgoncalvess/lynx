import subprocess
import time
from datetime import datetime


# Função para obter o tempo do último segundo registrado
def obter_ultimo_timestamp(log_file):
    try:
        command = f"tail -n 1 {log_file} | cut -d '[' -f 2 | cut -d ']' -f 1"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            result = result.stdout.strip()
            print(result)
            return datetime.strptime(result, '%d/%b/%Y:%H:%M:%S %z')

    except Exception as e:
        print(f"Erro ao enviar a data atual do log: {e}")
        return None


# Função para contar requisições por container no último segundo
def contar_requisicoes(log_file):
    last_timestamp = obter_ultimo_timestamp(log_file)

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
            #print(timestamp_str)
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')

            # Se a linha está dentro do último segundo, conta a requisição
            if timestamp == target_timestamp:
                # Captura o IP upstream
                upstream_ip = line.split('upstream: ')[1].split(',')[0].strip()
                print(upstream_ip)
                # Incrementa o contador para esse IP
                if upstream_ip in requests_count:
                    requests_count[upstream_ip] += 1
                else:
                    requests_count[upstream_ip] = 1

    # Exibe o resultado
    for ip, count in requests_count.items():
        print(f"{ip}, {count}")

while True:
    log_file = '/var/log/nginx/upstream_access.log'
    contar_requisicoes(log_file)
    print("---------------------------")
    time.sleep(3)
