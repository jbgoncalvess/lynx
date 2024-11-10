from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render
from apps.api.models import ContainerLxcImage
from apps.containers.views import create_client_ssh


@login_required
def images_view(request):
    images = ContainerLxcImage.objects.all()

    # Inicializa a lista de dados das imagens
    image_data = []

    # Itera sobre as imagens para coletar os dados
    for image in images:
        # Adiciona os dados da imagem à lista
        image_data.append({
            'image_name': image.image_name,
            'description': image.description,
            'architecture': image.architecture,
            'size': image.size,
            'upload_date': image.upload_date
        })
        print(image.upload_date)

    # Envia os dados como contexto para o modelo, para exibição
    return render(request, 'images/images.html', {
        'image_data': image_data,
    })


@login_required
@require_http_methods(['DELETE'])
def delete_image(request, image_name):
    try:
        client = create_client_ssh()
        try:
            command = f"lxc image delete {image_name}"
            _, _, stderr = client.exec_command(command)

            # Verifica se houve erro no comando
            error = stderr.read().decode()
            if error:
                print(f"Erro ao excluir imagem no servidor: {error}")
                return JsonResponse({"success": False, "message": "Erro ao excluir a imagem no servidor."},
                                    status=500)

            # Se não houve erro, exclui a imagem do banco de dados, pois eu removi ela
            ContainerLxcImage.objects.filter(image_name=image_name).delete()
            return JsonResponse({"success": True, "message": "Imagem excluída com sucesso."},
                                status=200)

        except Exception as ssh_error:
            print(f"Erro SSH: {ssh_error}")
            return JsonResponse({"success": False, "message": "Erro ao conectar ao servidor via SSH."},
                                status=500)

        finally:
            client.close()

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Erro interno: {str(e)}"},
                            status=500)

