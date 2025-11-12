from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Song

class SongAdmin(admin.ModelAdmin):
	list_display = ('title', 'artist', 'owner', 'created_at')
	search_fields = ('title', 'artist', 'owner__username')
