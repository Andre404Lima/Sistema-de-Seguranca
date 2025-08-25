from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

class LoginView(View):
    def get(self, request):
        # Exibe a página de login (formulário vazio)
        return render(request, 'core/login.html')

    def post(self, request):
        # Processa o envio do formulário de login
        user = authenticate(
            request, 
            username=request.POST.get('username'), 
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('dashboard')  # Se credenciais válidas, autentica o usuário e redireciona para o dashboard
        messages.error(request, 'Usuário ou senha inválidos')
        return render(request, 'core/login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
