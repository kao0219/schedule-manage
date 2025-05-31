from django.contrib import admin
from .models import Invite
from .models import Family
from .models import CustomUser, Family, Schedule, ScheduleComment, Invite
from .models import Memo
from django.utils.html import format_html
from .models import ScheduleCommentRead

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_token', 'status', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('status','family')
    search_fields = ('invite_token',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'family')
    fields = ('email', 'username', 'family', 'is_active', 'is_staff', 'is_superuser')

# 管理画面にfamily一覧で表示するために入力
class CustomUserInline(admin.TabularInline):
    model = CustomUser
    fields = ('username', 'email')
    extra = 0

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    inlines = [CustomUserInline]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id','schedule_title','user', 'schedule_memo', 'get_color_label', 'image_url', 'start_time', 'end_time', 'created_at')
    list_filter = ('user',)
    search_fields = ('schedule_title', 'user__email')

    def get_color_label(self, obj):
        return obj.get_color_label()
    get_color_label.short_description = '色'


@admin.register(ScheduleComment)
class ScheduleCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'content', 'created_at', 'display_date')
    search_fields = ('content',)

@admin.register(ScheduleCommentRead)
class ScheduleCommentReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment_id_display', 'is_deleted_display', 'created_at', 'updated_at') 

    def comment_id_display(self, obj):
        return obj.comment.id  
    comment_id_display.short_description = 'Comment ID'

    def is_deleted_display(self, obj):
        return 'True' if obj.is_deleted else 'False'
    is_deleted_display.short_description = 'Is Deleted'


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ('memo_title',  'user', 'content', 'image_tag', 'created_at')
    search_fields = ('memo_title', 'user__email')
    list_filter = ('user', 'created_at')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px;">', obj.image.url)
        return '-'
    image_tag.short_description = '画像'