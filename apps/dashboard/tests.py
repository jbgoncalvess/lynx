from django.core.cache import cache
from django.http import JsonResponse


def minha_view():
    # Alguma lógica
    cache.clear()  # Limpa o cache

    return JsonResponse({"message": "Cache limpo!"})
