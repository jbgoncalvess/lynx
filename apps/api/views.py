from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CurrentCount, DailyMaxMin, ContainerMetrics
from django.utils import timezone
import json


@csrf_exempt
def num_containers(request):
    if request.method == 'POST':
        try:
            # Adiciono o corpo da requisição a variável data e obtenho o número de containers ativos (30s)
            data = json.loads(request.body)
            container_count = data.get('active_containers')

            # Métodos para tratar o dado recebido nas tabelas do DB
            current_containers(container_count)
            max_min_containers(container_count)

            # Retorna uma resposta de sucesso
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid request'}, status=400)


def current_containers(container_count):
    # Adiciona um novo registro na tabela ContainerStatus (time é adiciona o atual do Br)
    CurrentCount.objects.create(container_count=container_count)
    # Manter apenas os últimos 3 registros de containers ativos para não acumular lixo
    if CurrentCount.objects.count() > 3:
        oldest_entry = CurrentCount.objects.order_by('time').first()
        oldest_entry.delete()


def max_min_containers(container_count):
    # Adicionar a data atual, pegando somente o ANO/MES/DIA
    current_date = timezone.localtime().date()
    # Verifico se tem algum registro nesse dia
    existing_entry = DailyMaxMin.objects.filter(date=current_date).first()

    # Se tiver registro, eu verifico se é o maior ou o menor do dia, só pode ser os dois se a tabela não existir
    # para aquele dia
    if existing_entry:
        if existing_entry.max_containers < container_count:
            existing_entry.max_containers = container_count
            existing_entry.save()

        elif existing_entry.min_containers > container_count:
            existing_entry.min_containers = container_count
            existing_entry.save()

    # Se não tiver registro, eu crio um novo com o valor que chegou, tanto para Min quanto para Max
    else:
        DailyMaxMin.objects.create(date=current_date, max_containers=container_count, min_containers=container_count)

    # Mantém no máximo 90 dias de registros
    if DailyMaxMin.objects.count() > 90:
        oldest_entry = DailyMaxMin.objects.order_by('date').first()
        oldest_entry.delete()

#######################################################################################################################
#######################################################################################################################


@csrf_exempt
def metrics_containers(request):
    if request.method == 'POST':
        try:
            # Lê o corpo da requisição
            data = json.loads(request.body)

            # Itera sobre as métricas de cada container
            for container in data:
                # Aqui, você pode querer implementar lógica para atualizar ou criar entradas
                # Exemplo: Criar ou atualizar um registro no banco de dados com base no nome do container
                container_name = container['name']
                cpu_usage = container['cpu_usage']
                ram_usage = container['ram_usage']

                print(f"NOME: {container_name}, CPU_USAGE:{cpu_usage} , RAM_USAGE:{ram_usage}.")

                existing_entry = DailyMaxMin.objects.filter(container_name=container_name).first()

                if existing_entry:
                    existing_entry.time = timezone.localtime
                    existing_entry.cpu_usage = cpu_usage
                    existing_entry.ram_usage = ram_usage
                    # existing_entry.rps =
                    # existing_entry.active_connections =
                    # existing_entry.http_errors =
                    # existing_entry.latency =
                else:
                    DailyMaxMin.objects.create(container_name=container_name, cpu_usage=cpu_usage, ram_usage=ram_usage,
                                               # rps=rps_usage, active_connections=active_connections,
                                               # http_errors=http_errors, http_errors=http_errors, latency=latency
                                               )

            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)
