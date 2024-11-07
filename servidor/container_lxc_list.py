import subprocess
import requests
import json
import time
import csv
from io import StringIO

url_lxc_list = 'http://192.168.77.1:8000/data_lxc_list/'
url_lxc_image = 'http://192.168.77.1:8000/data_lxc_image/'


# Função para coletar os dados detalhados do LXC list
def collect_lxc_list():
    try:
        # Executa o comando lxc list com as colunas necessárias
        command = "lxc list --format csv --columns n,s,4,6"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Converte o resultado em formato CSV
        csv_data = StringIO(result.stdout)
        reader = csv.reader(csv_data)

        # Estrutura para armazenar os dados dos containers
        containers = []

        # Itera sobre o CSV e coleta os dados
        for row in reader:
            if len(row) < 4:
                continue  # Ignora linhas incompletas ou mal formatadas

            # Tratamento para múltiplos IPs: separar múltiplos IPs por espaço ou vírgula
            ipv4_list = row[2].split() if row[2] else []
            ipv6_list = row[3].split() if row[3] else []

            container = {
                'name': row[0],
                'status': row[1],
                'ipv4': ipv4_list,  # Lista de IPv4
                'ipv6': ipv6_list   # Lista de IPv6
            }
            containers.append(container)

        return containers

    except Exception as e:
        print(f"Erro ao coletar dados do LXC: {e}")
        return []


def collect_lxc_image():
    # Executa o comando 'lxc image list' em formato CSV para coletar somente os dados necessários
    command = "lxc image list --format csv --columns ldasu"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout

    # Usa o módulo csv para ler os dados no formato CSV
    images = []
    csv_reader = csv.reader(StringIO(output))

    for row in csv_reader:
        if len(row) >= 5:  # Garante que todas as colunas necessárias estão presentes
            image_data = {
                'name': row[0],
                'description': row[1],
                'architecture': row[2],
                'size': row[3],
                'upload_date': row[4]
            }
            images.append(image_data)

    return images


# Função para enviar os dados para o software
def enviar_dados():
    # Coleta o número de containers ativos

    # Coleta os dados detalhados dos containers lxc_list e lxc_image_list
    containers_lxc_list = collect_lxc_list()
    containers_lxc_image = collect_lxc_image()

    print(containers_lxc_list)
    print("= * 100")
    print(containers_lxc_image)

    # Cabeçalhos para indicar que estamos enviando JSON
    headers = {'Content-Type': 'application/json'}

    # Envia os dados de containers_lxc_list para o Lynx
    try:
        response = requests.post(url_lxc_list, data=json.dumps(containers_lxc_list), headers=headers)
        if response.status_code == 200:
            print("Dados sobre lxc list enviados com sucesso!")
        else:
            print(f"Erro ao enviar dados sobre lxc list. Status: {response.status_code}, Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")

    # Envia os dados de containers_lxc_image para o Lynx
    try:
        response = requests.post(url_lxc_image, data=json.dumps(containers_lxc_image), headers=headers)
        if response.status_code == 200:
            print("Dados sobre lxc images enviados com sucesso!")
        else:
            print(f"Erro ao enviar dados sobre lxc images. Status: {response.status_code}, Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")


# Loop infinito para enviar os dados a cada 30 segundos
while True:
    enviar_dados()
    time.sleep(30)  # Aguarda 30 segundos antes de executar novamente

