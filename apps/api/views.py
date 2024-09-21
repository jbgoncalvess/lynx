from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContainerStatus, DailyMax, DailyMin
from django.utils import timezone
import json


@csrf_exempt
def info_containers(request):
    if request.method == 'POST':
        try:
            # Adiciono o corpo da requisição a variável data e obtenho o número de containers ativos (30s)
            data = json.loads(request.body)
            container_count = data.get('active_containers')

            # Métodos para tratar o dado recebido nas tabelas do DB
            current_containers(container_count)
            max_containers(container_count)
            min_containers(container_count)

            # Retorna uma resposta de sucesso
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid request'}, status=400)


def current_containers(container_count):
    # Adiciona um novo registro na tabela ContainerStatus (time é adiciona o atual do Br)
    ContainerStatus.objects.create(container_count=container_count)
    # Manter apenas os últimos 3 registros de containers ativos para não acumular lixo
    if ContainerStatus.objects.count() > 3:
        oldest_entry = ContainerStatus.objects.order_by('time').first()
        oldest_entry.delete()


def max_containers(container_count):
    # Adicionar a data atual, pegando somente o ANO/MES/DIA
    current_date = timezone.localtime().date()
    # Verifico se tem algum registro nesse dia
    existing_entry = DailyMax.objects.filter(date=current_date).first()

    # Se tiver registro, eu verifico se o valor dele é menor que o que chegou, se for menor troca e salva
    if existing_entry:
        if existing_entry.max_containers < container_count:
            existing_entry.max_containers = container_count
            existing_entry.save()
    # Se não tiver registro, eu crio um novo com o valor que chegou mesmo (Um valor baixo é maior que nada)
    else:
        DailyMax.objects.create(date=current_date, max_containers=container_count)

    # Mantém no máximo 90 dias de registros
    if DailyMax.objects.count() > 90:
        oldest_entry = DailyMax.objects.order_by('date').first()
        oldest_entry.delete()


def min_containers(container_count):
    # Mesma coisa que max_containers, mas com a lógica inversa, pois quero adicionar os valores menores
    current_date = timezone.localtime().date()
    existing_entry = DailyMin.objects.filter(date=current_date).first()

    if existing_entry:
        if existing_entry.min_containers > container_count:
            existing_entry.min_containers = container_count
            existing_entry.save()
    else:
        DailyMin.objects.create(date=current_date, min_containers=container_count)

    if DailyMin.objects.count() > 90:
        oldest_entry = DailyMin.objects.order_by('date').first()
        oldest_entry.delete()
