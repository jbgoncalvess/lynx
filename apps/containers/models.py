from django.db import models
from django.utils import timezone


class ContainerStatus(models.Model):
    # Campo para armazenar o número de containers ativos
    container_count = models.IntegerField(default=-1)

    # Campo para armazenar o timestamp de quando o registro foi criado
    hora = models.DateTimeField(default=timezone.now)

    # Opcionalmente, você pode adicionar um método para facilitar a leitura dos dados
    def __str__(self):
        return f"{self.container_count} containers ativos em {self.hora}"
