from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.api.models import ContainerStatus  # Certifique-se de que o import está correto


@login_required
def dashboard_view(request):
    ult_reg = ContainerStatus.objects.order_by('-hora').first()
    regs = ContainerStatus.objects.order_by('-hora')[:7]
    container_counts = [status.container_count for status in regs]
    container_counts.reverse()  # Reverte a lista para que o mais antigo fique na primeira posição

    # Envia os dados como uma variável de contexto para o template
    return render(request, 'dashboard/dashboard.html',
                  {'container_counts': container_counts, 'ult_reg': ult_reg})

