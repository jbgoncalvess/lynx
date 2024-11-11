from .models import ContainerMetrics, ContainerLxcList, ContainerLxcImage, ContainerIP

db = ContainerMetrics.objects.all()
print(db)
