from django.contrib import admin
from .models import Invite
from .models import Family
admin.site.register(Family)
from .models import CustomUser, Family, Schedule, ScheduleComment, Invite
from .models import Memo
from django.utils.html import format_html
from .models import ScheduleCommentRead

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_token', 'status', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('invite_token',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'family')
    fields = ('email', 'username', 'family', 'is_active', 'is_staff', 'is_superuser')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id','schedule_title', 'schedule_memo', 'get_color_label', 'image_url', 'start_time', 'end_time', 'created_at')
    search_fields = ('schedule_title',)

    def get_color_label(self, obj):
        return obj.get_color_label()
    get_color_label.short_description = '色'


@admin.register(ScheduleComment)
class ScheduleCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'content', 'created_at')
    search_fields = ('content',)

@admin.register(ScheduleCommentRead)
class ScheduleCommentReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'is_deleted', 'created_at', 'updated_at') 

    def comment_id_display(self, obj):
        return obj.comment.id  

    comment_id_display.short_description = 'Comment ID'  

@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ('memo_title', 'content', 'image_tag', 'created_at')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px;">', obj.image.url)
        return '-'
    image_tag.short_description = '画像'