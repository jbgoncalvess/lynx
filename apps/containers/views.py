from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ContainerStatus
import json


@login_required
def containers_view(request):
    # Passar o último valor que tenho no banco, ou seja, ultima atualização
    last_status = ContainerStatus.objects.order_by('-hora').first()
    # Enviar para o container.html essa atualização, não mandar direto do banco
    return render(request, 'containers/containers.html', {'last_status': last_status})


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
            if ContainerStatus.objects.count() > 3:
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