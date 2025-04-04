from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages 
from django.shortcuts import redirect

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
                return redirect('/app/home/') #ホーム画面へ
        except User.DoesNotExist:
            pass #とくにエラーメッセージなし

        #失敗した場合はログイン画面に戻る
        return redirect('/login/') 
 
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def home_view(request):
    return HttpResponse("<h1>ホーム画面</h1>")