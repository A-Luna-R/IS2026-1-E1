from django.urls import path
from . import views

urlpatterns = [
    path('upload-song', views.upload_song, name= 'upload-song'),
    path('songs-list', views.songs_list, name= 'songs-list'),
    path('delete/<int:song_id>', views.delete_song, name= 'delete-song'),
    path('like/<int:song_id>', views.toggle_like_user, name= 'songs_like_user'),
    path('liked', views.liked_songs, name= 'songs_liked'),
    path('explore', views.explore_songs, name='songs_explore'),
    path('<int:song_id>', views.song_detail, name='song_detail'),
]