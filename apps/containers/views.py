from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from .models import ContainerStatus
import json


@csrf_exempt
@login_required
def containers_view(request):
    # Obtém o status do container para o usuário atual
    # container_status = ContainerStatus.objects.filter(user=request.user).first()

    return render(request, 'containers/containers.html', {
        # 'container_status': container_status
    })


# @csrf_exempt
# # @login_required
# def info_containers(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             container_count = data.get('active_containers', 0)
#
#             # Salvar os dados no banco associando o container_count ao usuário atual
#             ContainerStatus.objects.create(
#                 container_count=container_count
#             )
#
#             return JsonResponse({'status': 'success'}, status=200)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#     return JsonResponse({'status': 'invalid request'}, status=400)
