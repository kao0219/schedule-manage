from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages 
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

User = get_user_model()

def index(request):
    return HttpResponse('<h1>schedule manage</h1>')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            #カスタムユーザーからメールで探す
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.email, password=password) #username→emailで認証

            if user is not None:
                login(request, user)
                return redirect('/home/') #ホーム画面へ
        except User.DoesNotExist:
            pass #とくにエラーメッセージなし

        #失敗した場合はログイン画面に戻る
        return redirect('/login/') 
 
    return render(request, 'login.html')

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]

        #ユーザー作成　パスは暗号化して保存
        CustomUser.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        return redirect("app:home") #登録完了ならホーム画面へ
    return render(request, 'signup.html')

def home_view(request):
    return render(request, 'home.html')

def memos_view(request):
    return render(request, 'memos.html')

def favorites_schedule_view(request):
    return render(request, 'favorites_schedule.html')

def favorites_memos_view(request):
    return render(request, 'favorites_memos.html')

def settings_view(request):
    return render(request, 'settings.html')

def logout_view(request):
    logout(request)
    return redirect('app:login') # ログアウト画面に戻る

def invite_member_view(request):
    return render(request, 'invite_member.html')

def change_password_view(request):
    return render(request, 'change_password.html')

@login_required
def change_email_view(request):
    return render(request, 'change_email.html')

def calender_mode_view(request):
    if request.method =='POST':
        selected_mode = request.POST.get('calender_mode')
        request.session['calender_mode'] = selected_mode
    return redirect('app:settings')

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('app:settings')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})
