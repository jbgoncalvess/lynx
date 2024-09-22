from django.db import models
from django.utils import timezone


class CurrentCount(models.Model):
    # Campo para armazenar o número de containers ativos
    container_count = models.IntegerField(default=0)

    # Campo para armazenar o timestamp de quando o registro foi criado
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.container_count} containers ativos em {self.time}"


# Model para armazenar os valores máximos por data
class DailyMax(models.Model):
    date = models.DateField(unique=True)
    max_containers = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.date}: {self.max_containers} containers"


# Model para armazenar os valores mínimos por data
class DailyMin(models.Model):
    date = models.DateField(unique=True)
    min_containers = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.date}: {self.min_containers} containers"


class ContainerMetrics(models.Model):
    container_id = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.localtime)

    cpu_usage = models.FloatField(default=0)
    ram_usage = models.FloatField(default=0)
    rps = models.IntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    http_errors = models.IntegerField(default=0)
    latency = models.FloatField(default=0)

    def __str__(self):
        return (f"Container {self.container_id} - {self.time} - CPU: {self.cpu_usage} - RAM: {self.ram_usage}"
                f" - RPS: {self.rps} - Active_conn: {self.active_connections} - HTTP: {self.http_errors}"
                f" - latency: {self.latency}")
