from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1>schedule manage</h1>')


def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')