from django.db import models
from django.utils import timezone
from django.db.models import JSONField


class HostContainersConnections(models.Model):
    active_containers = models.IntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Verifica se o número de registros é maior ou igual a 5
        if HostContainersConnections.objects.count() >= 5:
            # Exclui o registro mais antigo (com menor 'time')
            oldest_entry = HostContainersConnections.objects.order_by('time').first()
            oldest_entry.delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.active_containers} containers ativos em {self.time} | "
                f"Conexões ativas: {self.active_connections}")


class HostRps(models.Model):
    requests = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Verifica se o número de registros é maior ou igual a 16
        if HostRps.objects.count() >= 16:
            # Exclui o registro mais antigo (com menor 'time')
            oldest_entry = HostRps.objects.order_by('time').first()
            oldest_entry.delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Requests: {self.requests} em {self.time}"


# Model para armazenar os valores máximos e mínimos por data
class HostDailyMaxMin(models.Model):
    time = models.DateField(unique=True)
    max_containers = models.IntegerField(default=0)
    min_containers = models.IntegerField(default=0)

    def update_or_create_record(self):
        # Obtém a data atual (somente ano/mês/dia)
        current_date = timezone.localtime().date()

        # Verifica se já existe um registro para o dia atual
        existing_entry = HostDailyMaxMin.objects.filter(time=current_date).first()

        if existing_entry:
            # Se já existir um registro, comparamos os valores e atualizamos se necessário
            print(f"Registro encontrado para {current_date}, verificando se precisa ser atualizado.")

            # Atualiza max_containers se o valor atual for maior
            if self.max_containers > existing_entry.max_containers:
                existing_entry.max_containers = self.max_containers

            # Atualiza min_containers se o valor atual for menor
            if self.min_containers < existing_entry.min_containers:
                existing_entry.min_containers = self.min_containers

            # Salva as atualizações no banco de dados
            existing_entry.save()

        else:
            HostDailyMaxMin.objects.create(
                time=current_date,  # Usando a data atual
                max_containers=self.max_containers,
                min_containers=self.min_containers
            )

        # Verifica se o número de registros é maior ou igual a 7
        if HostDailyMaxMin.objects.count() > 7:
            # Exclui o registro mais antigo (com menor 'time')
            oldest_entry = HostDailyMaxMin.objects.order_by('time').first()
            print(f"Excluindo o registro mais antigo: {oldest_entry.time}")
            oldest_entry.delete()

    def __str__(self):
        return f"{self.time}: MAX: {self.max_containers} e MIN: {self.min_containers} containers"


# Model para armazenar as métricas dos containers
class ContainerMetrics(models.Model):
    container_name = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    cpu_usage = models.FloatField(default=0)
    ram_usage = models.FloatField(default=0)
    disk_usage = models.FloatField(default=0)
    uptime = models.IntegerField(default=0)
    processes = models.IntegerField(default=0)
    requests_c = JSONField(default=list, blank=True, null=True)

    def add_request_c(self, new_request):
        self.requests_c.append(new_request)
        if len(self.requests_c) > 4:
            self.requests_c.pop(0)
        self.save()

    def __str__(self):
        return (f"Container {self.container_name} - {self.time} - {self.active}"
                f" - CPU: {self.cpu_usage} - RAM: {self.ram_usage}"
                f" - Disco: {self.disk_usage} - Uptime: {self.uptime} - Processos: {self.processes}"
                f" - Request_container = {self.requests_c}")


# Model para armazenar o nome dos containers e seus status
class ContainerLxcList(models.Model):
    container_name = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30)

    def __str__(self):
        return f"Container {self.container_name} - {self.time} - STATUS: {self.status}"


# Model para adicionar os endereços IPs e a interface dos containers da classe ContainerLxcList,
# isso porque um container pode ter mais de um endereço IP, relação de um para vários, por isso a chave estrangeira
class ContainerIP(models.Model):
    IP_TYPE_CHOICES = [
        ('IPv4', 'IPv4'),
        ('IPv6', 'IPv6'),
    ]

    container = models.ForeignKey(ContainerLxcList, related_name='ips', on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=50)
    interface = models.CharField(max_length=30)  # interface de rede a qual aquele ip está atribuído
    ip_type = models.CharField(max_length=4, choices=IP_TYPE_CHOICES)

    def __str__(self):
        return f"IP {self.ip_address} ({self.ip_type}){self.interface} for container {self.container.container_name}"


class ContainerLxcImage(models.Model):
    image_name = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=150)
    architecture = models.CharField(max_length=30)
    size = models.CharField(max_length=30)
    upload_date = models.DateTimeField()

    def __str__(self):
        return (f"Container {self.image_name} - {self.time} - Description: {self.description}"
                f" - architecture: {self.architecture} - size: {self.size} - upload_date: {self.upload_date}")
