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
from datetime import date, time
from .forms import ScheduleForm
from .models import ScheduleComment
from .forms import CommentForm
from .forms import MemoForm
from django.core.paginator import Paginator
from datetime import datetime
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import ScheduleComment, ScheduleCommentRead

User = get_user_model()

def index(request):
    return HttpResponse('<h1>schedule manage</h1>')

def portfolio_view(request):
    return render(request, 'portfolio.html')


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
            pass #エラーメッセージなし

        #失敗した場合はログイン画面に戻る
        return redirect('/login/') 
 
    return render(request, 'login.html')

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]

        
        CustomUser.objects.create(
            email=email,
            username=username,
            password=make_password(password)
        )
        return redirect("app:home") #登録完了ならホーム画面へ
    return render(request, 'signup.html')

def home_view(request):
    return render(request, 'home.html')

def schedule_json_view(request):
    schedules = Schedule.objects.all()
    events = []
    
    # 未読コメントの予定ID一覧
    unread_schedule_ids = []
    if request.user.is_authenticated:
        read_ids = ScheduleCommentRead.objects.filter(
            user=request.user,
            is_deleted=False
        ).values_list('comment_id', flat=True)

        unread_comments = ScheduleComment.objects.exclude(id__in=read_ids).exclude(user=request.user)
        unread_schedule_ids = unread_comments.values_list('schedule_id', flat=True).distinct()


    for schedule in schedules:
        if schedule.start_time is None:
            continue

        event = {
            'id': schedule.id,
            'title': schedule.schedule_title,
            'start': schedule.start_time.date().isoformat(), 
            'color': schedule.get_color_code(),
        }
        
        
        # 未読なら🔔マークを見出しに表示
        if schedule.id in unread_schedule_ids:
            event['title'] += ' 🔔'

        events.append(event)

    return JsonResponse(events, safe=False)

def search_view(request):
    query = request.GET.get('q', '')
    schedules = Schedule.objects.filter(schedule_title__icontains=query) if query else []
    memos = Memo.objects.filter(memo_title__icontains=query) if query else []
    
    updated_memo_id = None

    if request.method == 'POST':
        memo_id = request.POST.get('memo_id')
        memo = get_object_or_404(Memo, id=memo_id)
        form = MemoForm(request.POST, request.FILES, instance=memo)
        if form.is_valid():
            form.save()
            updated_memo_id = memo_id

    for memo in memos:
        memo.form = MemoForm(instance=memo)

    context = {
        'query': query,
        'schedules': schedules,
        'memos': memos,
        'updated_memo_id' : updated_memo_id,
    }
    return render(request, 'search_results.html',context)


@login_required
def schedule_create_view(request):
    
    selected_date_str = request.GET.get('date') 
    # or datetime.now().date().isoformat() ←あとで戻すこの行を149行につける
    print("selected_date_str:", selected_date_str)

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    print("selected_date（変換後）:", selected_date) # 151～157後で消す

    # selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()　←あとで戻す
  
    username_initial = request.user.username[0].upper()

    now = datetime.now()
    start_hour = now.hour
    start_minute = now.minute   #日時反映部分
    
    # 開始終了時刻そろえる
    start_dt = datetime.combine(selected_date, time(start_hour, start_minute))
    

    initial_data = {
        'start_time': start_dt,
        'end_time': start_dt,
        'repeat_type': 0, # 繰り返し「なし」デフォルト
    }

    if request.method == 'POST' :
        form = ScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
        
            if schedule.is_all_day:
                # 終日なら開始時刻があればその日付を使って登録
                if schedule.start_time:
                    schedule.schedule_date = schedule.start_time.date()
                else:
                    schedule.schedule_date = selected_date
                    schedule.start_time = None
                    schedule.end_time = None
            else:
                if schedule.start_time:
                    schedule.schedule_date = schedule.start_time.date()
                else:
                    schedule.schedule_date = selected_date

            schedule.save()
            return redirect('app:home')  
        
        else:
            
            context = {
                'form': form,
                'selected_date': selected_date,
                'username_initial': username_initial,
                'now': now.strftime("%Y-%m-%dT%H:%M"),  
                'is_edit': False,
            }

            return render(request, 'schedule_create.html', context)
    else:
        form = ScheduleForm(initial=initial_data)
        context = {
            'form': form,
            'selected_date': selected_date,
            'username_initial': username_initial,
            'now': now.strftime("%Y-%m-%dT%H:%M"),
            'is_edit': False,
        }
        return render(request, 'schedule_create.html', context)    

@login_required
def schedule_detail_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit':
            form = ScheduleForm(request.POST, request.FILES, instance=schedule)
            comment_form = CommentForm()  
            if form.is_valid():
                schedule = form.save(commit=False)
                

                if schedule.is_all_day: 
                    #  開始時刻があればそれを日付を取得し登録
                    if schedule.start_time:
                        schedule.schedule_date = schedule.start_time.date()
                    else:
                        # なければ元のschedule日付か、なければ今日の日付いれる
                        schedule.schedule_date = schedule.schedule_date or timezone.now().date()
                    schedule.start_time = None
                    schedule.end_time = None  
                else:
                    if schedule.start_time:
                        schedule.schedule_date = schedule.start_time.date()
                    else:
                        schedule.schedule_date = None
                
                schedule.save()
                return redirect('app:home')  

        elif action == 'comment':
            form = ScheduleForm(instance=schedule)  
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.schedule = schedule
                comment.user = request.user
                comment.save()

    else:
        form = ScheduleForm(instance=schedule)
        comment_form = CommentForm()

    comments = ScheduleComment.objects.filter(schedule=schedule).order_by('-created_at')
    username_initial = schedule.user.username[:1].upper()

    if schedule.start_time:
        selected_date = schedule.start_time.strftime('%Y年%m月%d日（%a）')
    else:
        selected_date = ''


    return render(request, 'schedule_detail.html', {
        'form': form,
        'schedule': schedule,
        'comments': comments,
        'comment_form': comment_form,
        'username_initial': username_initial,
        'selected_date': selected_date,
        'is_edit': True,
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
            return redirect('app:schedule_detail', schedule_id=schedule_id)
        

@login_required
def comment_list_view(request):
    user = request.user
    comments = ScheduleComment.objects.exclude(user=user).order_by('-created_at') #他人のコメントだけ取得

    read_comment_ids = ScheduleCommentRead.objects.filter(
        user=request.user,
        is_deleted=False #　削除されていないものだけ
    ).values_list('comment_id', flat=True) #既読にしたコメントID取得
    
    context = {
        'comments': comments,
        'read_comment_ids': list(read_comment_ids),  
    }
    return render(request, 'comment_list.html', context)
    
@require_POST # コメント確認
def comment_confirm_view(request, comment_id):
    comment = get_object_or_404(ScheduleComment, id=comment_id)
    user = request.user

    #既読履歴なしである場合はis_deleted を False に戻す
    read_entry, created = ScheduleCommentRead.objects.get_or_create(
        user=user,
        comment=comment
    )

    if not created:
        # 未読で削除でも既読扱い
        read_entry.is_deleted = False
        read_entry.save()

    schedule_id = comment.schedule.id
    return redirect(reverse('app:schedule_detail', args=[schedule_id]))

@require_POST # コメント一覧から削除
def comment_list_delete_view(request, comment_id):
    user = request.user
    comment = get_object_or_404(ScheduleComment, id=comment_id)

    # 未読でも削除ボタン押下可能へ
    read_entry, created = ScheduleCommentRead.objects.get_or_create(
        user=user,
        comment=comment,
        defaults={'is_deleted': True}
    )
    
    if not created:
        read_entry.is_deleted = True
        read_entry.save()
        print("削除フラグ立てました")

    return redirect('app:comment_list_view')  # 一覧ページに戻る

def schedule_delete_view(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    schedule.delete()
    return redirect('app:home')


def memos_view(request):
    memos = Memo.objects.all().order_by('-created_at')  
    paginator = Paginator(memos, 8)  # 8件まで

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for memo in page_obj:
        memo.form = MemoForm(instance=memo)

    return render(request, 'memos.html', {
        'page_obj': page_obj,
    })


def create_memo_view(request):
    if request.method == 'POST':
        title = request.POST.get('memo_title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # 画像を取得

        Memo.objects.create(
            memo_title=title,
            content=content,
            image=image
        )
        return redirect('app:memos')  # メモ一覧へ

def memo_detail_view(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)

    if request.method == 'POST':
        form = MemoForm(request.POST, request.FILES, instance=memo)
        if form.is_valid():
            form.save()
            return redirect('app:memo_detail', memo_id=memo.id)
    else:
        form = MemoForm(instance=memo)

    return render(request, 'memo_detail.html', {'form': form, 'memo': memo})

def memo_delete_view(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    memo.delete()

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('app:memos')  # 削除後メモ一覧へ

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
