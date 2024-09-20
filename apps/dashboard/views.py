from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.api.models import ContainerStatus, DailyMax, DailyMin
import json


@login_required
def dashboard_view(request):
    # Obtém o último registro de containers ativos
    ult_reg = ContainerStatus.objects.order_by('-time').first()

    # Ordena as entradas pela data em ordem decrescente e pega os últimos 7 registros
    daily_max_data = DailyMax.objects.order_by('-date')[:7]
    daily_min_data = DailyMin.objects.order_by('-date')[:7]

    # Inverte a ordem para exibir as datas do mais antigo para o mais recente
    daily_max_data = daily_max_data[::-1]
    daily_min_data = daily_min_data[::-1]

    # Formata as datas e valores de containers para o gráfico
    dates = [entry.date.strftime('%d/%m') for entry in daily_max_data]  # Formata a data como 'dia/mês'
    max_container_counts = [entry.max_containers for entry in daily_max_data]
    min_container_counts = [entry.min_containers for entry in daily_min_data]

    # Passar vetor de string para o front-end js preciso converter com json.dumps
    # dates = ['13/09', '14/09', '15/09', '16/09', '17/09', '18/09', '19/09']
    # dates = ['13/09', '14/09']
    dates = json.dumps(dates)
    print(dates)
    # Inteiros não preciso converter
    # max_container_counts = [3, 4, 5, 2, 10, 11, 7]
    # max_container_counts = [7, 3]

    # Envia os dados como uma variável de contexto para o template
    return render(request, 'dashboard/dashboard.html', {
        'ult_reg': ult_reg,
        'dates': dates,
        'max_container_counts': max_container_counts,
        'min_container_counts': min_container_counts
    })