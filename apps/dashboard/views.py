from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.api.models import CurrentCount, DailyMaxMin, ContainerMetrics
import json
import re


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

    # Função para ordenar os nomes com natural sorting, ou seja, se tiver o 'c11' ele ficara depois do 'c2'
    # Ordenação por padrão do banco de dados é lexicográfica (troquei no código - Função pronta
    def natural_key(container):
        # Aplique a função natural_key ao atributo container_name
        return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', container.container_name)]

    # Ordene os próprios objetos ContainerMetrics pelo nome do container
    container_metrics = sorted(ContainerMetrics.objects.filter(active=True), key=natural_key)

    # Agora extraia as métricas após ordenar os objetos corretamente
    container_names = [container.container_name for container in container_metrics]
    time = [container.time for container in container_metrics]
    cpu_usages = [container.cpu_usage for container in container_metrics]
    ram_usages = [container.ram_usage for container in container_metrics]
    disk_usages = [container.disk_usage for container in container_metrics]
    uptime = [container.uptime for container in container_metrics]
    processes = [container.processes for container in container_metrics]
    rps = [container.rps for container in container_metrics]
    urt = [container.urt for container in container_metrics]
    rt = [container.rt for container in container_metrics]

    # Passar vetor de string para o front-end js preciso converter com json.dumps
    # Inteiros não preciso converter
    dates = json.dumps(dates)
    container_names = json.dumps(container_names)

    # Envia os dados como uma variável de contexto para o modelo
    return render(request, 'dashboard/dashboard.html', {
        'ult_reg': ult_reg,

        'dates': dates,
        'max_container_counts': max_container_counts,
        'min_container_counts': min_container_counts,

        'container_names': container_names,
        'time': time,
        'cpu_usages': cpu_usages,
        'ram_usages': ram_usages,
        'disk_usages': disk_usages,
        'uptime': uptime,
        'processes': processes,
        'rps': rps,
        'urt': urt,
        'rt': rt
    })
