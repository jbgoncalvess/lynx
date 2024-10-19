from django.db import models
from django.utils import timezone


# Model para armazenar o número de containers ativos
class CurrentCount(models.Model):
    # Campo para armazenar o número de containers ativos no momento
    container_count = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.container_count} containers ativos em {self.time}"


# Model para armazenar os valores máximos e mínimos por data
class DailyMaxMin(models.Model):
    date = models.DateField(unique=True)
    max_containers = models.IntegerField(default=0)
    min_containers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date}: MAX: {self.max_containers} e MIN: {self.min_containers} containers"


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
    rps = models.FloatField(default=0)
    urt = models.FloatField(default=0)
    rt = models.FloatField(default=0)

    def __str__(self):
        return (f"Container {self.container_name} - {self.time} - {self.active}"
                f" - CPU: {self.cpu_usage} - RAM: {self.ram_usage}"
                f" - Disco: {self.disk_usage} - Uptime: {self.uptime} - Processos: {self.processes}"
                f" - RPS: {self.rps} - URT: {self.urt} - RT: {self.rt}")


# Model para armazenar o nome dos containers e seus status
class ContainerLxcList(models.Model):
    container_name = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30)

    def __str__(self):  # Dois underscores antes e depois
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
