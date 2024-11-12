from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.api.models import HostContainersConnections, HostDailyMaxMin, ContainerMetrics, HostRps
import json
import re


@login_required
def dashboard_view(request):
    # Obter active_containers e número de conexões ativas
    active_containers = HostContainersConnections.objects.latest('time')
    active_containers = active_containers.active_containers

    time_active_connections = HostContainersConnections.objects.all().values('time', 'active_connections')

    times_active_connections = []
    active_connections = []
    for record in time_active_connections:
        time = record['time'].strftime('%H:%M:%S')
        times_active_connections.append(time)

        active_connections.append(record['active_connections'])

    # Obter as 15 requisições diminuir a i da i-1, somar i as suas tres vizinhas e dividir pelo número de segundos que
    # chega cada requisição, assim tenho o rps do host (balanceador)
    host_rps = HostRps.objects.order_by('time').values_list('requests', flat=True)[:15]
    # Capturar o tempo a cada 3, pois eu uso 3 valores do Host_rps para formar 1, que é RPS. Converter para HORA:MINUTO
    time_host_rps = HostRps.objects.order_by('time').values_list('time', flat=True)[2::3]
    times_host_rps = [time.strftime('%H:%M:%S') for time in time_host_rps]

    # Após diminuir i de i-1 e salvar
    # request_geral = [2, 2, 1, 2, 1, 1, 9, 4, 21, 7, 5, 7, 2, 4, 2]
    # O primeiro valor de rps será a soma dos primeiros 3 elementos de request_geral: 2 + 2 + 1 = 5
    # O segundo valor será a soma dos próximos 3 elementos: 2 + 1 + 1 = 4
    # O terceiro valor será a soma dos próximos 3 elementos: 9 + 4 + 21 = 34
    # O quarto valor será a soma dos próximos 3 elementos: 7 + 5 + 7 = 19
    # O quinto valor será a soma dos próximos 3 elementos: 2 + 4 + 2 = 8
    rps_host = []
    if host_rps:
        request_geral = [host_rps[1]-host_rps[0]]
        for i in range(1, len(host_rps)):
            request_geral.append(host_rps[i] - host_rps[i - 1])

        rps_host = [sum(request_geral[i:i + 3]) for i in range(0, len(request_geral), 3)]
        print(rps_host)

    # O times_host_rps pode ser menor que o host_rps, visto que se o numero de elementos de tempo nao for multiplo 3,
    # ele nao coleta na base de dados
    if len(times_host_rps) < len(host_rps):
        time_extra = HostRps.objects.latest('time')
        time_extra = time_extra.time.strftime('%H:%M:%S')
        times_host_rps.append(time_extra)
    print(times_host_rps)

    # Ordena as entradas pela data em ordem decrescente e pega os últimos 7 registros (26/08 - 25/08 ..)
    daily_max_min = HostDailyMaxMin.objects.order_by('-time')[:7]
    daily_max_min = daily_max_min[::-1]

    # Formata as datas e valores de containers para o gráfico
    dates = [entry.time.strftime('%d/%m') for entry in daily_max_min]  # Formata a data como 'dia/mês'
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
    request_c = [container.requests_c for container in container_metrics]

    rps_containers = []
    for sublist in request_c:
        # Calculando as diferenças consecutivas
        diff = [sublist[i] - sublist[i - 1] for i in range(1, len(sublist))]
        # Somando as diferenças
        rps_containers.append(sum(diff))

    print("REQUESTS C")
    print(rps_containers)
    # Passar vetor de string para o front-end js preciso converter com json.dumps
    # Inteiros não preciso converter
    dates = json.dumps(dates)
    container_names = json.dumps(container_names)

    times_active_connections = json.dumps(times_active_connections)

    times_host_rps = json.dumps(times_host_rps)

    print('TESTES')
    print(times_host_rps)
    print(rps_host)

    # Envia os dados como uma variável de contexto para o modelo
    return render(request, 'dashboard/dashboard.html', {
        'active_containers': active_containers,
        'active_connections': active_connections,  # NOVO ADD LOGO MAIS
        'time_active_connections': times_active_connections,  # NOVO ADD LOGO MAIS

        'rps_host': rps_host,
        'times_host_rps': times_host_rps,

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
        'rps_containers': rps_containers  # NOVO, ADD LOGO MAIS
    })
