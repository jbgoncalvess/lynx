from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def images_view(request):

    # Envia os dados como contexto para o template
    return render(request, 'images/images.html', {})
