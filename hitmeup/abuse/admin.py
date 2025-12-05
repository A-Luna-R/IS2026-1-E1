from django.contrib import admin

# Register your models here.

from .models import SongReport

class SongReportAdmin(admin.ModelAdmin):
    list_display = ('id','song','reason','status','created_at','reporter_user','reporter_artist','resolved_by','resolved_at')
    list_filter = ('status','reason','created_at')
    search_fields = ('song__title','reporter_user__username','reporter_artist__stage_name','details','resolution_notes')
