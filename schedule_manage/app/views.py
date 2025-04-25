from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages 
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomPasswordChangeForm
from .forms import CustomEmailChangeForm
import uuid
from django.utils import timezone
from .models import Invite
from .forms import CustomUserCreationForm
from django.utils.dateparse import parse_date
from .models import Schedule, Memo
from datetime import date
from .forms import ScheduleForm
from .models import ScheduleComment
from .forms import CommentForm
from .forms import MemoForm


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
            user = authenticate(request, username=user_obj.email, password=password) #username→ユーザー名で認証

            if user is not None:
                print("ログイン成功")
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

def search_view(request):
    query = request.GET.get('q', '')
    schedules = Schedule.objects.filter(schedule_title__icontains=query) if query else []
    memos = Memo.objects.filter(memo_title__icontains=query) if query else []

    context = {
        'query': query,
        'schedules': schedules,
        'memos': memos,
    }
    return render(request, 'search_results.html',context)

@login_required
def schedule_create_view(request):
    selected_date = request.GET.get('date') or date.today().isoformat()
    username_initial = request.user.username[0].upper()

    if request.method == 'POST':
        form = ScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
            # 登録後も同じページを表示
            return render(request, 'schedule_create.html', {
                'form': ScheduleForm(),
                'date': selected_date,
                'username_initial': username_initial,
            })
    else:
        form = ScheduleForm()

    return render(request, 'schedule_create.html', {
    'form': form,
    'date': selected_date,
    'username_initial': username_initial,
    })

@login_required
def schedule_detail_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        form = ScheduleForm(request.POST, request.FILES, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('home')  # 必要に応じて変更
    else:
        form = ScheduleForm(instance=schedule)

    comments = ScheduleComment.objects.filter(schedule=schedule).order_by('-created_at')
    comment_form = CommentForm()

    return render(request, 'schedule_detail.html', {
        'form': form,
        'schedule': schedule,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def comment_add_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.schedule = schedule
            comment.save()
            return redirect('schedule_detail', schedule_id)

def comment_list_view(request):
    return render(request, 'comment_list.html')


def memos_view(request):
    return render(request, 'memos.html')

def create_memo_view(request):
    if request.method == 'POST':
        title = request.POST.get('memo_title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # 画像を取得！

        Memo.objects.create(
            memo_title=title,
            content=content,
            image=image
        )
        return redirect('app:memos')  # 名前空間ありならこちらに修正

def memo_detail_view(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)

    if request.method == 'POST':
        form = MemoForm(request.POST, request.FILES, instance=memo)
        if form.is_valid():
            form.save()
            return redirect('memos')  # 編集完了後はメモ一覧へ戻る
    else:
        form = MemoForm(instance=memo)

    return render(request, 'memo_detail.html', {'form': form, 'memo': memo})


@login_required
def settings_view(request):
    family_members = User.objects.filter(family=request.user.family)
    return render(request, 'settings.html', {'members': family_members})

def logout_view(request):
    logout(request)
    return redirect('app:login') # ログアウト画面に戻る

def invite_member_view(request):
    invite_url = None

    if request.method == 'POST':
        token = str(uuid.uuid4())
        invite = Invite.objects.create(
            invite_token=token,
            status=1, #　未使用
            expires_at = timezone.now() + timezone.timedelta(days=1) # 有効期限1日後に
        )
        invite_url = request.build_absolute_uri(f'/invite/{token}/') # URL作成

    return render(request, 'invite_member.html', {'invite_url': invite_url})

def invite_register_view(request, token):
    invite = get_object_or_404(Invite, invite_token=token)
    
    # 有効期限　or　使用済みのチェック
    if invite.status != 1 or invite.expires_at < timezone.now():
        return render(request, 'invite_invalid.html', {'token': token}) # 無効なURL画面

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # 一時保存
            user.family = invite.family # 招待に紐づいたファミリーをセット
            user.save()                 # 保存
            invite.status = 2           # 使用済みへ
            invite.save()
            return redirect('home') #　ホームへ遷移
    else:
        form = CustomUserCreationForm()

    return render(request, 'invite_register.html', {'form': form, 'token': token}) #　有効な場合は登録画面

def change_password_view(request):
    return render(request, 'change_password.html')

@login_required
def change_email_view(request):
    if request.method == 'POST':
        form = CustomEmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            request.user.email = new_email
            request.user.save()
            return redirect('app:home')
    else:
            form = CustomEmailChangeForm(user=request.user, initial={'currnet_email': request.user.email})

    return render(request, 'change_email.html', {'form': form})

def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            print("パスワード変更成功")
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('app:home')
        else:
            print("バリデーションエラー：" ,form.errors)

    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})
