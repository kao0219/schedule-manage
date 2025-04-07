from django.contrib import admin
from .models import Invite

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('invite_token', 'status', 'expires_at', 'create_at', 'update_at')
    list_filter = ('status',)
    search_fields = ('invite_token',)