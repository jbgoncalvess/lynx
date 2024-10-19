from apps.api.models import ContainerLxcList


def buscar_status(container_name = "c1"):
    try:
        container = ContainerLxcList.objects.get(container_name=container_name)
        print(container.status)
    except ContainerLxcList.DoesNotExist:
        return None

buscar_status()
