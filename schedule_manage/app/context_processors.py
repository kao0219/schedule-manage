#予定コメントマーク表示のため作成
from .models import ScheduleComment, ScheduleCommentRead 

def unread_comment_flag(request):
    if request.user.is_authenticated:
        read_ids = ScheduleCommentRead.objects.filter(user=request.user).values_list('comment_id', flat=True)
        has_unread = ScheduleComment.objects.exclude(id__in=read_ids).exists()
    else:
        has_unread = False

    return {
        'has_unread_comment': has_unread
    }