from django.db import models
from django.utils import timezone


class CurrentCount(models.Model):
    # Campo para armazenar o número de containers ativos no momento
    container_count = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.container_count} containers ativos em {self.time}"


# Model para armazenar os valores máximos e mínimos por data
class DailyMaxMin(models.Model):
    date = models.DateField(unique=True)
    max_containers = models.IntegerField(default=0)
    min_containers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date}: MAX: {self.max_containers} e MIN: {self.min_containers} containers"


class ContainerMetrics(models.Model):
    container_name = models.CharField(max_length=100, unique=True)
    time = models.DateTimeField(default=timezone.localtime)

    cpu_usage = models.FloatField(default=0)
    ram_usage = models.FloatField(default=0)
    rps = models.IntegerField(default=0)
    active_connections = models.IntegerField(default=0)
    http_errors = models.IntegerField(default=0)
    latency = models.FloatField(default=0)

    def __str__(self):
        return (f"Container {self.container_name} - {self.time} - CPU: {self.cpu_usage} - RAM: {self.ram_usage}"
                f" - RPS: {self.rps} - Active_conn: {self.active_connections} - HTTP: {self.http_errors}"
                f" - latency: {self.latency}")
