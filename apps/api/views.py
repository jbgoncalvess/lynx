from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContainerStatus, DailyMax, DailyMin
from django.utils import timezone
import json


@csrf_exempt
def info_containers(request):
    if request.method == 'POST':
        try:
            # Adiciono o corpo da requisição a variável data
            data = json.loads(request.body)

            # Obtém o número de containers ativos enviado pela VM
            container_count = data.get('active_containers')

            # Adiciona um novo registro na tabela ContainerStatus
            ContainerStatus.objects.create(container_count=container_count)

            # Mantém no máximo 3 registros de ContainerStatus (Não juntar lixo)
            if ContainerStatus.objects.count() > 3:
                oldest_entry = ContainerStatus.objects.order_by('time').first()
                if oldest_entry:
                    oldest_entry.delete()

            # Obtém a data atual
            current_date = timezone.localtime().date()

            # print(current_date)

            # Tenta buscar o registro existente para a data atual
            existing_entry = DailyMax.objects.filter(date=current_date).first()

            # print(existing_entry)
            if existing_entry:
                # Se já houver um registro, verificar se o novo valor é maior
                if container_count > existing_entry.max_containers:
                    # Atualiza o valor máximo de containers para aquele dia
                    existing_entry.max_containers = container_count
                    existing_entry.save()
            else:
                # Se não houver um registro, cria um novo
                DailyMax.objects.create(date=current_date, max_containers=container_count)

            existing_entry = DailyMin.objects.filter(date=current_date).first()
            if existing_entry:
                if container_count < existing_entry.min_containers:
                    existing_entry.min_containers = container_count
                    existing_entry.save()
            else:
                DailyMin.objects.create(date=current_date, min_containers=container_count)



            # Verifica se há mais de 90 registros no total (3 meses tá bom de histórico)
            if DailyMax.objects.count() > 90:
                # Se houver mais de 90, apaga o registro mais antigo
                oldest_entry = DailyMax.objects.order_by('date').first()
                if oldest_entry:
                    oldest_entry.delete()

            # Retorna uma resposta de sucesso
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid request'}, status=400)
