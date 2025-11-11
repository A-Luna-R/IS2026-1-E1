from django.urls import path
from . import views

urlpatterns = [
    path('list', views.playlists_list, name= 'playlists_list'),
    path('<int:playlist_id>', views.playlist_detail, name= 'playlist_detail'),
    path('search', views.playlists_search, name= 'playlists_search'),
    path('artist/<int:artist_id>/love', views.artist_love_playlist, name= 'playlist_artist_love'),
    path('artist/<int:artist_id>/love/sync', views.artist_love_sync, name= 'playlist_artist_love_sync'),
]
