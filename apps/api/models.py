from django.db import models
from django.utils import timezone


# Armazenar valor atual de container rodando
class ContainerStatus(models.Model):
    # Campo para armazenar o número de containers ativos
    container_count = models.IntegerField(default=0)

    # Campo para armazenar o timestamp de quando o registro foi criado
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.container_count} containers ativos em {self.time}"


# Model para armazenar os valores máximos por data
class DailyMax(models.Model):
    # Campo para armazenar a data do registro
    date = models.DateField(unique=True)
    max_containers = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.localtime)

    def __str__(self):
        return f"{self.date}: {self.max_containers} containers"
