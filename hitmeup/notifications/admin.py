from django.contrib import admin

# Register your models here.
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','verb','recipient_user','recipient_artist','is_read','created_at')
    list_filter = ('is_read','created_at')
    search_fields = ('verb','message','recipient_user__username','recipient_artist__stage_name')

