from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContainerStatus
import json


# API para minha VM enviar as informações dos containers para o software
@csrf_exempt
def info_containers(request):
    if request.method == 'POST':
        try:
            # Adiciono o corpo da requisição a variável data
            data = json.loads(request.body)

            # Obtém o número de containers ativo enviado pela VM
            container_count = data.get('active_containers')

            # Adiciona um novo registro
            ContainerStatus.objects.create(container_count=container_count)

            # Mantém no máximo 3 registros
            if ContainerStatus.objects.count() > 7:
                # Obtém o registro mais antigo e o exclui
                oldest_entry = ContainerStatus.objects.order_by('hora').first()
                if oldest_entry:
                    oldest_entry.delete()

            # Retorna uma resposta de sucesso
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            # Em caso de erro, retorna uma resposta de erro com a mensagem
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Se o método da requisição não for POST, retorna uma resposta inválida
    return JsonResponse({'status': 'invalid request'}, status=400)