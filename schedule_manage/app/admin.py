from django.contrib import admin
from .models import Invite
from .models import Family
admin.site.register(Family)
from .models import CustomUser, Family, Schedule, ScheduleComment, Invite


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
    list_display = ('id','schedule_title', 'start_time', 'end_time', 'created_at')
    search_fields = ('schedule_title',)

@admin.register(ScheduleComment)
class ScheduleCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'content', 'comment_status', 'created_at')
    search_fields = ('content',)