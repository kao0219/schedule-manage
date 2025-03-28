from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
     path('login', views.index, name='index'),
]
