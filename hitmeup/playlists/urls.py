from django.urls import path
from . import views

urlpatterns = [
    path('liked', views.playlists_liked, name= 'playlists_liked'),
    path('list-playlists', views.playlists_list, name= 'list-playlists'),
    path('<int:playlist_id>', views.playlist_detail, name= 'playlist'),
    path('search-lists', views.playlists_search, name= 'search-lists'),
    path('artist/<int:artist_id>/love', views.artist_love_playlist, name= 'playlist_artist_love'),
    path('artist/<int:artist_id>/love/sync', views.artist_love_sync, name= 'playlist_artist_love_sync'),
    path('new', views.create_playlist_user, name='playlist_create_user'),
    path('new/artist', views.create_playlist_artist, name='playlist_create_artist'),
    path('delete/<int:playlist_id>', views.delete_playlist_user, name='playlist_delete_user'),
    path('delete/artist/<int:playlist_id>', views.delete_playlist_artist, name= 'playlist_delete_artist'),
    path('like/user/<int:playlist_id>', views.playlist_toggle_like_user, name= 'playlist_like_user'),
    path('like/artist/<int:playlist_id>', views.playlist_toggle_like_artist, name= 'playlist_like_artist'),

]
