from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.

def homePage(request):
    return render(request, 'main/home.html')

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
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
        return redirect('home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect('home')
    context = {'loginForm': form}
    return render(request, 'main/login.html', context)

@login_required(login_url='login')
def profilePage(request):
    return render(request, 'main/profile.html')

def UserLogout(request):
    logout(request)
    return redirect('home')
