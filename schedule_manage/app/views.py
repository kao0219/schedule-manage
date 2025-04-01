from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages 

def index(request):
    return HttpResponse('<h1>schedule manage</h1>')


def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')