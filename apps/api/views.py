from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CurrentCount, DailyMaxMin, ContainerMetrics, ContainerLxcList, ContainerIP
from django.utils import timezone
import json


@csrf_exempt
def data_lxc_list(request):
    if request.method == 'POST':
        try:
            # Converte o conteúdo da requisição JSON para dicionário
            data = json.loads(request.body)

            # Extraio o número de containers ativos, insere no banco e compara com max e min
            active_containers = data.get('active_containers', 0)
            current_containers(active_containers)
            max_min_containers(active_containers)

            # Extrai a lista de containers e seus detalhes
            containers = data.get('containers', [])
            print(containers)

            # Processa cada container recebido
            for container_data in containers:
                container_name = container_data.get('name')
                status = container_data.get('status', 'UNKNOWN')
                ipv4_list = container_data.get('ipv4', [])
                ipv6_list = container_data.get('ipv6', [])

                # Verifica se o container já existe no banco de dados e cria/atualiza
                container, created = ContainerLxcList.objects.update_or_create(
                    container_name=container_name,
                    defaults={
                        'status': status,
                        'time': timezone.now(),
                    }
                )

                # Remove os IPs antigos associados ao container se já existiam
                if not created:
                    container.ips.all().delete()

                # Adiciono endereços IPv4. Avança a cada 2, já que recebo os dados "IPV4, interface".
                for i in range(0, len(ipv4_list), 2):  # A lista de ipv4 alterna entre IP e interface
                    ip_address = ipv4_list[i]
                    interface = ipv4_list[i + 1]  # A interface está no índice seguinte
                    ContainerIP.objects.create(
                        container=container,
                        ip_address=ip_address,
                        interface=interface,  # Ajuste se a interface variar
                        ip_type='IPv4',
                    )

                # Adiciono endereços IPV6. Avança a cada 2, já que recebo os dados "IPV6, interface".
                for i in range(0, len(ipv6_list), 2):  # A lista de ipv6 alterna entre IP e interface
                    ip_address = ipv6_list[i]
                    interface = ipv6_list[i + 1]  # A interface está no índice seguinte
                    ContainerIP.objects.create(
                        container=container,
                        ip_address=ip_address,
                        interface=interface,  # Ajuste se a interface variar
                        ip_type='IPv6',
                    )

            return JsonResponse({"message": "Dados recebidos e salvos com sucesso."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)


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
        DailyMaxMin.objects.create(
            date=current_date,
            max_containers=container_count,
            min_containers=container_count,
        )

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
            container_names = []
            # Itera sobre as métricas de cada container
            for container in data:
                # Exemplo: Criar ou atualizar um registro no banco de dados com base no nome do container
                # Crio uma lista, pois os container que nao vir eu activate = false
                container_names.append(container['name'])
                cpu_usage = container['cpu_usage']
                ram_usage = container['ram_usage']
                disk_usage = container['disk_usage']
                uptime = container['uptime']
                processes = container['processes']
                rps = container['rps']
                urt = container['urt']
                rt = container['rt']

                print(f"NOME: {container_names[-1]}, CPU_USAGE:{cpu_usage} , RAM_USAGE:{ram_usage}"
                      f" , DISK_USAGE:{disk_usage}, UPTIME: {uptime}, PROCESSES: {processes}, RPS: {rps}, URT: {urt}, "
                      f" RT: {rt}.")

                existing_entry = ContainerMetrics.objects.filter(container_name=container_names[-1]).first()

                if existing_entry:
                    existing_entry.time = timezone.localtime()
                    existing_entry.active = True
                    existing_entry.cpu_usage = cpu_usage
                    existing_entry.ram_usage = ram_usage
                    existing_entry.disk_usage = disk_usage
                    existing_entry.uptime = uptime
                    existing_entry.processes = processes
                    existing_entry.rps = rps
                    existing_entry.urt = urt
                    existing_entry.rt = rt
                    existing_entry.save()
                else:
                    ContainerMetrics.objects.create(
                        container_name=container_names[-1],
                        cpu_usage=cpu_usage,
                        ram_usage=ram_usage,
                        disk_usage=disk_usage,
                        uptime=uptime,
                        processes=processes,
                        rps=rps,
                        urt=urt,
                        rt=rt,
                    )

            (ContainerMetrics.objects.filter(active=True).exclude(container_name__in=container_names)
             .update(active=False))
            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


#######################################################################################################################
#######################################################################################################################
