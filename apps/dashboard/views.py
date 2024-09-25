from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.api.models import CurrentCount, DailyMaxMin, ContainerMetrics
import json


@login_required
def dashboard_view(request):
    # Obtém o último registro de containers ativos
    ult_reg = CurrentCount.objects.order_by('-time').first()

    # Ordena as entradas pela data em ordem decrescente e pega os últimos 7 registros (26/08 - 25/08 ..)
    daily_max_min = DailyMaxMin.objects.order_by('-date')[:7]
    daily_max_min = daily_max_min[::-1]

    # Formata as datas e valores de containers para o gráfico
    dates = [entry.date.strftime('%d/%m') for entry in daily_max_min]  # Formata a data como 'dia/mês'
    max_container_counts = [entry.max_containers for entry in daily_max_min]
    min_container_counts = [entry.min_containers for entry in daily_max_min]

    # Passar vetor de string para o front-end js preciso converter com json.dumps
    # Inteiros não preciso converter
    dates = json.dumps(dates)
    print(dates)

    container_metrics = ContainerMetrics.objects.order_by('container_name')
    container_names = [container.container_name for container in container_metrics]
    cpu_usages = [container.cpu_usage for container in container_metrics]
    ram_usages = [container.ram_usage for container in container_metrics]
    disk_usages = [container.disk_usage for container in container_metrics]

    container_names = json.dumps(container_names)

    print(container_names, cpu_usages, ram_usages, disk_usages)



    # Envia os dados como uma variável de contexto para o template
    return render(request, 'dashboard/dashboard.html', {
        'ult_reg': ult_reg,

        'dates': dates,
        'max_container_counts': max_container_counts,
        'min_container_counts': min_container_counts,

        'container_names': container_names,
        'cpu_usages': cpu_usages,
        'ram_usages': ram_usages,
        'disk_usages': disk_usages
    })
