from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'accounts/homepage.html')

def contact(request):
    return HttpResponse('Contact Page')

def signin(request):
    return render(request, 'accounts/signin.html')

def signup(request):
    return render(request, 'accounts/signup.html')