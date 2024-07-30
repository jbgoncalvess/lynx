from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomLoginForm  # Importando o formulário personalizado


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirecionar para a página inicial ou qualquer página desejada
            else:
                form.add_error(None, 'Usuário ou senha inválidos')
    else:
        form = CustomLoginForm()
    return render(request, 'contas/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']  # Corrigido para 'password1'
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'contas/registro.html', {'form': form})
