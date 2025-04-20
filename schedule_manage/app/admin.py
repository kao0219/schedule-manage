from django.contrib import admin
from .models import Invite
from .models import Family
admin.site.register(Family)
from .models import CustomUser, Family

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_token', 'status', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('invite_token',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'family')
    fields = ('email', 'username', 'family', 'is_active', 'is_staff', 'is_superuser')
