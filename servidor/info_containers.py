import requests
import json
import subprocess
import time

# URL da minha API (view separada do software com "crsf except")
url = 'http://192.168.2.135:8000/info_containers/'


# Função para contar o número de containers ativos usando um comando bash
def contar_containers_ativos():
    try:
        result = subprocess.run(['lxc', 'list', '--format', 'csv', '--columns', 's'], capture_output=True, text=True)
        status_list = result.stdout.strip().split('\n')
        # Contando quantos containers estão no estado "RUNNING"
        containers_ativos = sum(1 for status in status_list if status == 'RUNNING')
        #containers_ativos = 7
        print(containers_ativos)
        return containers_ativos
    except Exception as e:
        print(f"Erro ao contar containers: {e}")
        return -1

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