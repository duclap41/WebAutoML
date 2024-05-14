from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreateUserForm


@login_required(login_url='signin')
def home(request):
    return render(request, 'accounts/homepage.html')

def contact(request):
    return HttpResponse('Contact Page')

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # return redirect('home')
                return render(request, 'accounts/homepage.html')

            else:
                messages.info(request, 'Username hoặc mật khẩu không đúng')
                # return render(request, 'accounts/signin.html', context)


    context = {}
    return render(request, 'accounts/signin.html', context)

def logoutUser(request):
    logout(request)
    return redirect('signin')

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Tài khoản ' + user + ' đã được tạo thành công')

    context = {'form':form}
    return render(request, 'accounts/signup.html', context)