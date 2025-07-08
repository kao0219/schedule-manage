from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.home, name='home'), # トップページ(ポートフォリオ)
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('calendar_info/', views.calendar_info_view, name='calendar_info'),
    path('schedule/json/', views.schedule_json_view, name='schedule_json'),
    path('search/', views.search_view, name='search'),
    path('memos/', views.memos_view, name='memos'),
    path('memos/create/', views.create_memo_view, name='create_memo'),
    path('memo/<int:memo_id>/', views.memo_detail_view, name='memo_detail'),
    path('memo/<int:memo_id>/delete/', views.memo_delete_view, name='memo_delete'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('invite_member/', views.invite_member_view, name='invite_member'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('change_email/', views.change_email_view, name='change_email'),
    path('invite/<str:token>/', views.invite_register_view, name='invite_register'),
    path('schedule/create/', views.schedule_create_view, name='schedule_create'),
    path('comments/', views.comment_list_view, name='comment_list_view'),
    path('comments/delete/<int:comment_id>/', views.comment_list_delete_view, name='comment_list_delete'),
    path('comments/confirm/<int:comment_id>/', views.comment_confirm_view, name='comment_confirm'),
    path('schedule/<int:schedule_id>/', views.schedule_detail_view, name='schedule_detail'),
    path('schedule/<int:schedule_id>/comment/', views.comment_add_view, name='comment_add'),
    path('schedule/<int:pk>/delete/', views.schedule_delete_view, name='schedule_delete'),

    
]
