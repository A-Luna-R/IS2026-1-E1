from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Playlist, PlaylistSong

class PlaylistSongInline(admin.TabularInline):
    model =PlaylistSong
    extra = 0

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
    inlines = [PlaylistSongInline]

class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'song', 'added_at')
    search_fields = ('playlist__name', 'song__title', 'song__owner__username')
