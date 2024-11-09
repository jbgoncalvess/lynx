from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import re

# Data no formato inicial
upload_date = "Aug 26, 2024 at 8:40am (UTC)"

# Converte a string para datetime
try:
    upload_date = timezone.datetime.strptime(upload_date, "%b %d, %Y at %I:%M%p (UTC)")

    print(upload_date)
    # Extrai o mês (abreviado ou completo, conforme desejar)
    mes_abreviado = upload_date.strftime("%b")  # Mês abreviado, ex: "Aug"
    mes_completo = upload_date.strftime("%B")  # Mês completo, ex: "August"

    print("Mês abreviado:", mes_abreviado)
    print("Mês completo:", mes_completo)

except ValueError as e:
    print("Erro ao converter data:", e)
