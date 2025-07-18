from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.

def homePage(request):
    return render(request, 'main/home.html')

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'registerForm': form}
    return render(request, 'main/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('')
    context = {'loginForm': form}
    return render(request, 'main/login.html', context)

@login_required(login_url='login')
def profilePage(request):
    return render(request, 'main/profile.html')

def UserLogout(request):
    auth.logout(request)
    return redirect('')
