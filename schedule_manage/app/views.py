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
from .models import Family
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
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden




User = get_user_model()

def index(request):
    return HttpResponse('<h1>Schedule Manage</h1>')

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
                login(request, user)
                return redirect('/home/') #ホーム画面へ
            else:
                messages.error(request, 'メールアドレスまたはパスワードが間違っています。') 
        except User.DoesNotExist:
            messages.error(request, 'ユーザーが存在しません。')
 
    return render(request, 'login.html')

def signup_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "このメールアドレスは既に登録されています。")
            return render(request, 'signup.html')
        
        if len(password) < 8:
            messages.error(request, "パスワードは8文字以上で入力してください。")
            return render(request, 'signup.html')

        # ファミリー作成
        family = Family.objects.create()

        # ユーザー作成
        user = CustomUser.objects.create(
            email=email,
            username=username,
            password=make_password(password),
            family=family
        )

        login(request, user)

        return redirect("app:home") #登録完了ならホーム画面へ
    return render(request, 'signup.html')

@login_required
def home_view(request):
    schedules = Schedule.objects.filter(user__family=request.user.family)

    for schedule in schedules:
        create_next_schedule_if_needed(schedule) # 繰り返し部分

    schedules = Schedule.objects.filter(user=request.user).order_by('start_time')

    return render(request, 'home.html', {'schedules': schedules})

    

# カレンダー表示について管理
def schedule_json_view(request):
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = datetime.now().date()
    #　ファミリー制限
    schedules = Schedule.objects.filter(user__family=request.user.family)

    events = []
    # 未読コメントの予定ID一覧
    unread_schedule_ids = []
    if request.user.is_authenticated:
        read_ids = ScheduleCommentRead.objects.filter(
            user=request.user
            
        ).values_list('comment_id', flat=True)

        unread_comments = ScheduleComment.objects.exclude(
            id__in=read_ids
        ).exclude(
            user=request.user
        )
        unread_schedule_ids = unread_comments.values_list(
            'schedule_id', flat=True
        ).distinct()


    for schedule in schedules:
        if schedule.start_time is None:
            continue

        event = {
            'id': schedule.id,
            'title': schedule.schedule_title,
            'start': schedule.start_time.date().isoformat(), # ←これは消すとうまくカレンダー反映されない
            'end': schedule.end_time.isoformat(), #121end~と123all~がないとカレンダーに日跨ぎの予定がうまく表示されない。
            'color': schedule.get_color_code(),
            'allDay': schedule.is_all_day, 
        }
        
        
        # 未読なら🔔マークを見出しに表示
        if schedule.id in unread_schedule_ids:
            event['title'] = '🔔'+ event['title']

        events.append(event)

    return JsonResponse(events, safe=False)

# 繰り返し部分
def create_next_schedule_if_needed(schedule):
    # ① 予定がすでに削除されていないか確認（DBに存在するか）
    if not Schedule.objects.filter(id=schedule.id).exists():
        return  # 削除されているなら終了　ここのチェックで作成止まる
  
    # ② 「なし」なら次は作成しない
    if schedule.repeat_type == 0:  # 0 →「なし」　ここのチェックで作成止まる
        return
    # ③ 今の予定完了しないと次は作らない
    if schedule.start_time > datetime.now():
        return
    
    # ④ 次の予定がすでに存在していれば作らない（未来の1件あればOK、無限に作られないため）
    future_exists = Schedule.objects.filter(
        user=schedule.user,
        schedule_title=schedule.schedule_title,
        start_time__gt=schedule.start_time
    ).exists()
    
    if future_exists:
        return  # すでに次の予定が存在する
    
    #リレー済みなら新規作成しない
    if schedule.is_relay_created:
        return

    # ⑤ 次の予定を作成する
    next_start = schedule.start_time
    next_end = schedule.end_time

    if schedule.repeat_type == 1:  # 毎日
        next_start += timedelta(days=1)
        next_end += timedelta(days=1)

    elif schedule.repeat_type == 2:  # 毎週
        next_start += timedelta(weeks=1)
        next_end += timedelta(weeks=1)
    
    elif schedule.repeat_type == 3:  # 毎月
        month = next_start.month + 1 if next_start.month < 12 else 1
        year = next_start.year + (next_start.month // 12)
        next_start = next_start.replace(year=year, month=month)
        next_end = next_end.replace(year=year, month=month)

    Schedule.objects.create(
        user=schedule.user,
        schedule_title=schedule.schedule_title,
        schedule_memo=schedule.schedule_memo,
        start_time=next_start,
        end_time=next_end,
        repeat_type=schedule.repeat_type,
        is_all_day=schedule.is_all_day,
        color=schedule.color,
        image_url=schedule.image_url,
    )
    #リレー済みにする
    schedule.is_relay_created = True
    schedule.save()

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
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = datetime.now().date()

    username_initial = request.user.username[0].upper()
    now = datetime.now()
    start_hour = now.hour
    start_minute = now.minute   #日時反映部分
    
    # 開始終了時刻そろえる
    start_dt = datetime.combine(selected_date, time(start_hour, start_minute))

    if request.method == 'POST' :
        form = ScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.is_all_day = 'is_all_day' in request.POST
        
            if schedule.is_all_day :
                schedule.schedule_date = selected_date
                schedule.start_time = datetime.combine(selected_date, time.min)
                schedule.end_time = datetime.combine(selected_date, time(23,59))
            else:
                if schedule.start_time and schedule.end_time:
                    # print(f"[DEBUG] start_time: {schedule.start_time}, end_time: {schedule.end_time}") 
                    schedule.schedule_date = schedule.start_time.date()

                    if schedule.start_time.date() != schedule.end_time.date():
                        schedule.repeat_type = '0'  # 「なし」に強制
                        # print("[DEBUG] 日跨ぎのため、repeat_typeを'なし'に設定")

                    if schedule.start_time > schedule.end_time: # ここで日跨ぎもOK
                        form.add_error('end_time', '終了日時は開始日時と同じか、それ以降に設定してください。')
                        context = {
                            'form': form,
                            'selected_date': selected_date,
                            'username_initial': username_initial,
                            'now': now.strftime("%Y-%m-%dT%H:%M"),
                            '_is_edit': False,
                            'start_time': schedule.start_time,
                            'end_time': schedule.end_time,
                        }
                        return render(request, 'schedule_create.html', context)
                else:
                    form.add_error(None, '開始日時と終了日時は必須です。')
                    context = {
                        'form': form,
                        'selected_date': selected_date,
                        'username_initial': username_initial,
                        'now': now.strftime("%Y-%m-%dT%H:%M"),
                        '_is_edit': False,
                        'start_time': start_dt,
                        'end_time': start_dt,
                    }
                    return render(request, 'schedule_create.html', context)
            print(f"[DEBUG] repeat_type before save: {schedule.repeat_type}")
            schedule.save()
            return redirect('app:home') 
        else:
            print("[DEBUG] フォームエラー:", form.errors.as_json())


    else:
        form = ScheduleForm(initial={
            'start_time': start_dt,
            'end_time': start_dt,
            'repeat_type': 0,  # 繰り返しはデフォルト「なし」
        })
    
      # 英語 → 日本語の曜日マップ
    WEEKDAYS_JA = ['月', '火', '水', '木', '金', '土', '日']
    weekday_japanese = WEEKDAYS_JA[selected_date.weekday()]
    context = {
        'selected_date': selected_date,
        'weekday_japanese': weekday_japanese,
        'form': form,
        'selected_date': selected_date,
        'username_initial': username_initial,
        'now': now.strftime("%Y-%m-%dT%H:%M"),
        '_is_edit': False,
        'start_time': start_dt,
        'end_time': start_dt,
    }
    return render(request, 'schedule_create.html', context)
    
@login_required
def schedule_detail_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    #　ファミリー制限
    if schedule.user.family != request.user.family:
        return HttpResponseForbidden("この予定にはアクセスできません")

    # クリックされた日付を取得
    clicked_date_str = request.GET.get('date')
    if clicked_date_str:
        try:
            date_obj = datetime.strptime(clicked_date_str, '%Y-%m-%d')
        except ValueError: 
            date_obj = schedule.start_time or timezone.now() 
    else: 
        date_obj = schedule.start_time or timezone.now() 
    
    display_date = date_obj.date()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit':
            form = ScheduleForm(request.POST, request.FILES, instance=schedule)
            comment_form = CommentForm()  
            if form.is_valid():
               
                schedule = form.save(commit=False)
                schedule.is_all_day = 'is_all_day' in request.POST
                
                #繰り返し設定の変更チェック　「なし」に変更ならリレー停止
                if schedule.repeat_type == 0:
                    schedule.is_relay_created = False
                else:
                    if not schedule.is_relay_created:
                        schedule.is_relay_created = True

                if schedule.is_all_day: 
                    #  開始時刻があればそれを日付を取得し登録
                    if schedule.start_time and schedule.end_time:
                        schedule.schedule_date = schedule.start_time.date()
                    else:
                        schedule.schedule_date = schedule.schedule_date or timezone.now().date()
            
                    schedule.start_time = datetime.combine(schedule.schedule_date, time.min)
                    schedule.end_time = datetime.combine(schedule.schedule_date, time(23,59))
                else:
                    # 通常の時間指定
                    if schedule.start_time and schedule.end_time:
                        schedule.schedule_date = schedule.start_time.date()
                    else:
                        schedule.schedule_date = schedule.schedule_date or timezone.now().date()
        
                schedule.save()
                return redirect('app:home')  

        elif action == 'comment':
            print("コメント処理に入った")
            form = ScheduleForm(instance=schedule)  
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                print("コメントフォームが有効") 
                comment = comment_form.save(commit=False)
                comment.schedule = schedule
                comment.user = request.user
                display_date_str = request.POST.get('display_date') #←
                print("display_date_str:", display_date_str)
                try:
                    comment.display_date = datetime.strptime(display_date_str, '%Y-%m-%d').date()
                except ValueError:
                    comment.display_date = timezone.now().date()
                print("保存する comment.display_date =", comment.display_date)
                comment.save()
                print("コメント保存完了！")

    else:
        form = ScheduleForm(instance=schedule)
        comment_form = CommentForm()

    filter_date = date_obj.date()
    print("フィルター用日付 filter_date:", filter_date)

    comments = ScheduleComment.objects.filter(
        schedule=schedule,
        # display_date=filter_date   #←これを入れるとコメント保存されても予定ページに表示されない
    ).order_by('-created_at')
    print("表示対象のコメント数 =", comments.count())
    print("コメント取得用 date_obj:", date_obj)
    print("フィルタ用 display_date:", date_obj.date())

    for comment in comments:
        if comment.user != request.user:  # 自分以外のコメントに限定
            read_entry, created = ScheduleCommentRead.objects.get_or_create(
                user=request.user,
                comment=comment
            )
            #すでに削除済みなら復元せずにスキップ
            if read_entry.is_deleted:
                continue
            #新規作成された場合　or　未削除のときだけread_atを更新    
            if not created:  
                read_entry.read_at = timezone.now()
                read_entry.save()

    username_initial = schedule.user.username[:1].upper()
    WEEKDAYS_JA = {
    'Mon': '月',
    'Tue': '火',
    'Wed': '水',
    'Thu': '木',
    'Fri': '金',
    'Sat': '土',
    'Sun': '日',
    }
        
    # 曜日を漢字表示
    weekday_en = date_obj.strftime('%a')
    weekday_ja = WEEKDAYS_JA.get(weekday_en, weekday_en)
    display_label = date_obj.strftime(f'%Y年%m月%d日（{weekday_ja}）')  
    
    # 開始日のラベル
    start_weekday_en = schedule.start_time.strftime('%a')
    start_weekday_ja = WEEKDAYS_JA.get(start_weekday_en, start_weekday_en)
    start_date_label = schedule.start_time.strftime(f'%m月%d日（{start_weekday_ja}）')

    # 終了日のラベル
    end_weekday_en = schedule.end_time.strftime('%a')
    end_weekday_ja = WEEKDAYS_JA.get(end_weekday_en, end_weekday_en)
    end_date_label = schedule.end_time.strftime(f'%m月%d日（{end_weekday_ja}）')

    # 日跨ぎなら開始〜終了、それ以外は開始のみ
    if schedule.start_time.date() == schedule.end_time.date():
        schedule_range_label = start_date_label
    else:
        schedule_range_label = f"{start_date_label} 〜 {end_date_label}"


    #DB保存・比較用
    display_date = date_obj.strftime('%Y-%m-%d')

    return render(request, 'schedule_detail.html', {
        'form': form,
        'schedule': schedule,
        'comments': comments,
        'comment_form': comment_form,
        'username_initial': username_initial,
        'display_date': display_date, 
        'selected_date': display_label, 
        'is_edit': True,
        'schedule_range_label': schedule_range_label,
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
    
    # 一覧から削除されたコメントIDを取得（非表示にする用）
    deleted_comment_ids = ScheduleCommentRead.objects.filter(
        user=user,
        is_deleted=True
    ).values_list('comment_id', flat=True)

    comments = (
        ScheduleComment.objects.exclude(user=user) 
        .exclude(id__in=deleted_comment_ids) 
        .filter(schedule__user__family=request.user.family) # ファミリー制限
        .order_by('-created_at') #他人のコメントだけ取得
    )

    read_comment_ids = ScheduleCommentRead.objects.filter(
        user=user,
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
    schedule_id = comment.schedule.id
    
    # 削除済み含めて既読履歴を取得
    read_entry = ScheduleCommentRead.objects.filter(user=user, comment=comment).first()

    # 削除済みの既読履歴があれば、既読処理せず戻る
    if read_entry and read_entry.is_deleted:
        return redirect(reverse('app:schedule_detail', args=[schedule_id]))

    # 履歴がなければ新規作成
    if not read_entry:
        read_entry = ScheduleCommentRead.objects.create(
            user=user,
            comment=comment,
            read_at=timezone.now(),
            is_deleted=False
        )
    else:
        # 既に履歴あり、未削除なら read_at を更新
        read_entry.read_at = timezone.now()
        read_entry.save()

    return redirect(reverse('app:schedule_detail', args=[schedule_id]))
    

@require_POST # コメント一覧から削除
def comment_list_delete_view(request, comment_id):
    user = request.user
    comment = get_object_or_404(ScheduleComment, id=comment_id)
    read_entry = ScheduleCommentRead.objects.get(user=request.user, comment=comment)
    read_entry.is_deleted = True
    read_entry.save()

    return redirect('app:comment_list_view')
       
   
def schedule_delete_view(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    # ファミリー制限
    if schedule.user.family != request.user.family:
        return HttpResponseForbidden("この予定は削除できません")
    schedule.delete()
    return redirect('app:home')

#メモ一覧
def memos_view(request):
    memos = Memo.objects.filter(user__family=request.user.family).order_by('-created_at')  

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
            image=image,
            user=request.user #誰がメモを作ったかを記録
        )
        return redirect('app:memos')  # メモ一覧へ
    

# 編集フォームデータ読み込みと保存、完了後にモーダル→一覧への処理
def memo_detail_view(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    #ファミリー制限
    if memo.user.family != request.user.family:
        return HttpResponseForbidden("このメモにはアクセスできません")
    
    if request.method == 'POST':
        form = MemoForm(request.POST, request.FILES, instance=memo)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200) # JSで処理しリダイレクト不要
        else:
            print(form.errors)           
    else:
        form = MemoForm(instance=memo)
    # ここが無いと GET時に return なしでエラーになる
    return render(request, 'components/memo_modal.html', {
        'form': form,
        'memo': memo,
    })


def memo_delete_view(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)

    #　ファミリーが一致していなければ削除できない
    if memo.user.family != request.user.family:
        return HttpResponseForbidden("このメモは削除できません")

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
            family=request.user.family,
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
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'パスワードが一致しません。')
        elif len(password1) < 8:
            messages.error(request, 'パスワードは8文字以上にしてください。')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'このメールアドレスはすでに使われています。')
        else:

            user = CustomUser.objects.create(
                email=email,
                username=username,
                password=make_password(password1),
                family = invite.family  # 招待に紐づいたファミリーをセット
            )
            invite.status = 2           # 使用済みへ
            invite.save()
            return redirect('app:home') #　ホームへ遷移   
    return render(request, 'invite_register.html', {'token': token}) #　有効な場合は登録画面

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
            form = CustomEmailChangeForm(user=request.user, initial={'current_email': request.user.email})

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
