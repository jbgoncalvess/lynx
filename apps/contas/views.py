from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import Registro


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'contas/login.html', {'error': 'Usuário e/ou senha inválidos'})
    return render(request, 'contas/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        form = Registro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = Registro()
    return render(request, 'contas/registro.html', {'form': form})
