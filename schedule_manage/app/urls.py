from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('memos/', views.memos_view, name='memos'),
    path('memos/create/', views.create_memo_view, name='create_memo'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('invite_member/', views.invite_member_view, name='invite_member'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('change_email/', views.change_email_view, name='change_email'),
    path('invite/<str:token>/', views.invite_register_view, name='invite_register'),
    path('schedule/create/', views.schedule_create_view, name='schedule_create'),
    path('comments/', views.comments_list_view, name='comments_list_view'),

]
