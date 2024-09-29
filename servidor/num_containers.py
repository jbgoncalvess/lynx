# Neste código eu coleto as métricas que envolvem a máquina host do servidor e não os containers

import requests
import json
import subprocess
import time

# URL da minha API (view separada do software com "crsf except")
url = 'http://192.168.2.135:8000/num_containers/'


# Função para contar o número de containers ativos usando um comando do shell
def contar_containers_ativos():
    try:
        command = "lxc list --format csv --columns s | grep -c RUNNING"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(int(result.stdout.strip()))
        return int(result.stdout.strip())
    except Exception as e:
        print(f"Erro ao contar containers: {e}")
        return 0


# Função para enviar os dados para o software
def enviar_dados():
    # Enviar os dados como dicionário pra facilitar na hora de eu pegar os dados
    data = {
        'active_containers': contar_containers_ativos()
    }

    # Cabeçalhos para indicar que estamos enviando JSON
    headers = {'Content-Type': 'application/json'}

    # Enviar os dados para o software
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("Dados enviados com sucesso!")
        else:
            print(f"Erro ao enviar dados. Status: {response.status_code}, Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")


# Loop infinito para enviar os dados a cada 30 segundos
while True:
    enviar_dados()
    time.sleep(30)  # Aguarda 30 segundos antes de executar novamente
