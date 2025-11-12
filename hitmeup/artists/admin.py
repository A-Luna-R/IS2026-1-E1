from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Artist, ArtistSongLike

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('stage_name','is_public')
    search_fields = ('stage_name',)

class ArtistSongLikeAdmin(admin.ModelAdmin):
    list_display = ('artist','song','created_at')
    search_fields = ('artist__stage_name','song__title','song__owner__username')
