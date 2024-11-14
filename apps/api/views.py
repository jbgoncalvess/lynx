from datetime import timedelta
import locale
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HostContainersConnections, HostRps, HostDailyMaxMin, ContainerMetrics, ContainerLxcList, ContainerIP, ContainerLxcImage
from django.utils import timezone
import json
import re
from django.conf import settings
from apps.nginx.views import check_cpu_usage


def host_metrics(active_containers, active_connections, rps):
    # Adiciona um novo registro na tabela ContainerStatus (time é adiciona o atual do Br)
    HostContainersConnections.objects.create(container_count=active_containers, active_connections=active_connections, rps=rps)
    # Manter apenas os últimos 3 registros de containers ativos para não acumular lixo
    if HostContainersConnections.objects.count() > 3:
        oldest_entry = HostContainersConnections.objects.order_by('time').first()
        oldest_entry.delete()


#######################################################################################################################
@csrf_exempt
def lxc_list(request):
    if request.method == 'POST':
        client_auth = request.headers.get('Authorization')
        if client_auth != f'Token {settings.AUTH_TOKEN}':
            return JsonResponse({"error": "Não autorizado"}, status=401)
        try:
            # Converte o conteúdo da requisição JSON para dicionário
            data = json.loads(request.body)

            # Extrai os nomes dos containers recebidos
            container_names = {container_data.get('name') for container_data in data}

            # Remove containers do banco que não estão na nova lista recebida
            ContainerLxcList.objects.exclude(container_name__in=container_names).delete()

            # Processa cada container recebido para atualizar/criar registros no banco
            for container_data in data:
                container_name = container_data.get('name')
                status = container_data.get('status', 'UNKNOWN')
                ipv4_list = container_data.get('ipv4', [])
                ipv6_list = container_data.get('ipv6', [])

                # Cria ou atualiza o container com os novos dados
                container, created = ContainerLxcList.objects.update_or_create(
                    container_name=container_name,
                    defaults={
                        'status': status,
                        'time': timezone.now(),
                    }
                )

                # Remove IPs antigos associados ao container, se já existiam
                if not created:
                    container.ips.all().delete()

                # Adiciona endereços IPv4
                for i in range(0, len(ipv4_list), 2):
                    ip_address = ipv4_list[i]
                    interface = re.sub(r'[()]', '', ipv4_list[i + 1])
                    ContainerIP.objects.create(
                        container=container,
                        ip_address=ip_address,
                        interface=interface,
                        ip_type='IPv4',
                    )

                # Adiciona endereços IPv6
                for i in range(0, len(ipv6_list), 2):
                    ip_address = ipv6_list[i]
                    interface = re.sub(r'[()]', '', ipv6_list[i + 1])
                    ContainerIP.objects.create(
                        container=container,
                        ip_address=ip_address,
                        interface=interface,
                        ip_type='IPv6',
                    )

            return JsonResponse({"message": "Dados recebidos e salvos com sucesso."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao decodificar o JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)


#######################################################################################################################


#######################################################################################################################
@csrf_exempt
def lxc_image(request):
    if request.method == 'POST':
        client_auth = request.headers.get('Authorization')
        if client_auth != f'Token {settings.AUTH_TOKEN}':
            return JsonResponse({"error": "Não autorizado"}, status=401)
        try:
            data = json.loads(request.body)

            # Nomes das imagens recebidas
            containers_images = {image.get('name') for image in data}

            # Remove containers do banco que não estão na nova lista recebida
            ContainerLxcImage.objects.exclude(image_name__in=containers_images).delete()

            for image in data:
                image_name = image.get('name')
                description = image.get('description')
                architecture = image.get('architecture')
                size = image.get('size')
                upload_date = image.get('upload_date')

                # Aqui eu altero o Locale temporariamente, pois no padrão do meu projeto, ele está em PT_BR, e aqui eu
                # preciso dele em inglês para converter a string para data (string formatada em ing de lxc_image_list)
                locale.setlocale(locale.LC_TIME, 'C')

                try:
                    # Converte a data para datetime no locale em inglês
                    upload_date = timezone.datetime.strptime(upload_date, "%b %d, %Y at %I:%M%p (UTC)")
                    upload_date = timezone.make_aware(upload_date, timezone.get_current_timezone())

                except ValueError:
                    return JsonResponse({"error": f"Erro ao converter data: {upload_date}"}, status=400)
                finally:
                    # Após resolver isso, retorno o locale para português
                    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

                # Agora que o locale original voltou, eu defino o horário como o do sistema
                upload_date = upload_date - timedelta(hours=3)

                # Salva no banco de dados
                ContainerLxcImage.objects.update_or_create(
                    image_name=image_name,
                    defaults={
                        'description': description,
                        'architecture': architecture,
                        'size': size,
                        'upload_date': upload_date
                    }
                )

            return JsonResponse({"message": "Dados recebidos e salvos com sucesso."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Erro ao decodificar JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)


#######################################################################################################################


#######################################################################################################################
@csrf_exempt
def metrics(request):
    if request.method == 'POST':
        client_auth = request.headers.get('Authorization')
        if client_auth != f'Token {settings.AUTH_TOKEN}':
            return JsonResponse({"error": "Não autorizado"}, status=401)
        try:
            data = json.loads(request.body)
            active_containers = data.get('active_containers', 0)
            active_connections = data.get('active_connections', 0)
            request = data.get('request', 0)
            containers_metrics = data.get('metrics_containers', [])

            container_names = {container_data.get('name') for container_data in containers_metrics}
            ContainerMetrics.objects.exclude(container_name__in=container_names).delete()

            # Número de containers ativos, conexões ativas no servidor e requisições feitas por segundo
            # Cria uma nova instância de HostContainersConnections
            HostContainersConnections.objects.create(
                active_containers=active_containers,
                active_connections=active_connections
            )

            HostRps.objects.create(requests=request)

            max_min = HostDailyMaxMin(max_containers=active_containers,min_containers=active_containers)
            max_min.update_or_create_record()

            cpu_usage_values = []
            container_names = []
            # Itera sobre as métricas de cada container
            for container in containers_metrics:
                # Exemplo: Criar ou atualizar um registro no banco de dados com base no nome do container
                # Crio uma lista, pois os container que nao vir eu activate = false
                container_names.append(container['name'])
                cpu_usage = container['cpu_usage']
                ram_usage = container['ram_usage']
                disk_usage = container['disk_usage']
                uptime = container['uptime']
                processes = container['processes']
                request_c = container['request_c']

                print(f"NOME: {container_names[-1]}, CPU_USAGE:{cpu_usage} , RAM_USAGE:{ram_usage}"
                      f" , DISK_USAGE:{disk_usage}, UPTIME: {uptime}, PROCESSES: {processes}, REQUESTS_C: {request_c}")

                cpu_usage_values.append(container['cpu_usage'])

                existing_entry = ContainerMetrics.objects.filter(container_name=container_names[-1]).first()
                print('TESTANDO-123')
                print(request_c)




                if existing_entry:
                    existing_entry.time = timezone.localtime()
                    existing_entry.active = True
                    existing_entry.cpu_usage = cpu_usage
                    existing_entry.ram_usage = ram_usage
                    existing_entry.disk_usage = disk_usage
                    existing_entry.uptime = uptime
                    existing_entry.processes = processes
                    existing_entry.add_request_c(request_c)
                    print(request_c)
                    existing_entry.save()
                else:
                    ContainerMetrics.objects.create(
                        container_name=container_names[-1],
                        cpu_usage=cpu_usage,
                        ram_usage=ram_usage,
                        disk_usage=disk_usage,
                        uptime=uptime,
                        processes=processes,
                        requests_c=[request_c]
                    )

            # Chamar a função para verificar se a média aritmética de cpu_usage é maior que 70% ou menor
            check_cpu_usage(cpu_usage_values)

            host = HostContainersConnections.objects.all()
            print(host)

            container = ContainerMetrics.objects.all()
            print(container)

            rps = HostRps.objects.all()
            print(rps)

            (ContainerMetrics.objects.filter(active=True).exclude(container_name__in=container_names)
             .update(active=False))
            return JsonResponse({'status': 'success'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido'}, status=405)
#######################################################################################################################
