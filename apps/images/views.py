from django.shortcuts import render
from apps.api.models import ContainerLxcImage
from django.utils import timezone


def images_view(request):
    # Obtém todas as imagens salvas no banco de dados
    images = ContainerLxcImage.objects.all()

    # Inicializa a lista de dados das imagens
    image_data = []

    # Itera sobre as imagens para coletar os dados
    for image in images:
        # Converte a data de upload para o fuso horário local

        # Adiciona os dados da imagem à lista
        image_data.append({
            'image_name': image.image_name,
            'description': image.description,
            'architecture': image.architecture,
            'size': image.size,
            'upload_date': image.upload_date
        })
        print(image.upload_date)

    # Envia os dados como contexto para o template
    return render(request, 'images/images.html', {
        'image_data': image_data,
    })
