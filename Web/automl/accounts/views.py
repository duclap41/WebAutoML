from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CreateUserForm, ChangeUserForm, UploadUserFileForm
from django.urls import reverse_lazy

import io
import pandas as pd
from AutoML import *
import urllib, base64



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

@login_required(login_url='signin')
def editprofile(request):
    if request.method == 'POST':
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Tài khoản ' + user + ' đã được cập nhật thành công')
    else:
        form = ChangeUserForm(instance=request.user) 

    context = {'form':form}
    return render(request, 'accounts/editprofile.html', context)

@login_required
def upload(request):
   # upload file
    if request.method == 'POST':
        form = UploadUserFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.user = request.user  # Gán user đang đăng nhập
            user_file.save()
            messages.info(request, 'Upload File thành công')
            return redirect('upload')  # Thay thế 'success_url' bằng URL thực tế của bạn
    else:
        form = UploadUserFileForm()
        
    # load file data to table
    df = pd.read_csv("D:\\ie221_project\\WebAutoML\\Data\\vehicle.csv")
    columns = df.columns.tolist()
    data = []
    for _, row in df.iterrows():
        data.append(row.tolist())

    context = {'form': form,
              'data': data,
              'columns' columns
              }
    return render(request, 'accounts/upload.html', context)

def model(request):
    context = {}
    return render(request, 'accounts/model.html', context)

def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)

def download(request):
    context = {}
    return render(request, 'accounts/download.html', context)

def overview(request):
    eda = EDA(pd.read_csv("D:\\ie221_project\\WebAutoML\\Data\\vehicle.csv"))
    num_ft = len(eda.columns)
    num_samp = eda.entries
    # add graphic to wen
    _, plot = eda.correlation(visual=True)
    buffer = io.BytesIO()
    plot.savefig(buffer, format='png')
    buffer.seek(0)
    img_plot = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(img_plot)
    graphic = graphic.decode('utf-8')

    context = {'num_features':num_ft,
               'num_samples':num_samp,
               'graphic':graphic
               }
    return render(request, 'accounts/overview.html', context)

def alert(request):
    context = {}
    return render(request, 'accounts/alert.html', context)

def reproduction(request):
    context = {}
    return render(request, 'accounts/reproduction.html', context)