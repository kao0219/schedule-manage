from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('memos/', views.memos_view, name='memos'),
    path('favorites/schedule/', views.favorites_schedule_view, name='favorites_schedule'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
]
