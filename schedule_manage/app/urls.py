from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
     path('hello', views.index, name='index'),
]
