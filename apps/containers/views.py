from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def containers_view(request):
    return render(request, 'containers/containers.html')