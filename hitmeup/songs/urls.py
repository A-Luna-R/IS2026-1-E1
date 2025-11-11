from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('upload-song', views.upload_song, name= 'upload-song'),
    path('songs-list', views.songs_list, name= 'songs-list'),
    path('delete/<int:song_id>', views.delete_song, name= 'delete-song'),
=======
<<<<<<< HEAD
    path('upload', views.upload_song, name= 'songs_upload'),
    path('list', views.songs_list, name= 'songs_list'),
    path('delete/<int:song_id>', views.delete_song, name= 'songs_delete'),
>>>>>>> 7401da3 (refactor: integración de ramas)
    path('like/<int:song_id>', views.toggle_like_user, name= 'songs_like_user'),
    path('liked', views.liked_songs, name= 'songs_liked'),
<<<<<<< HEAD
    path('explore', views.explore_songs, name='songs_explore'),
    path('<int:song_id>', views.song_detail, name='song_detail'),
=======
=======
    path('upload-song', views.upload_song, name= 'upload-song'),
    path('songs-list', views.songs_list, name= 'songs-list'),
    path('delete/<int:song_id>', views.delete_song, name= 'delete-song'),
>>>>>>> 9b90f7f (refactor: integración de ramas)
>>>>>>> c1005b0 (refactor: integración de ramas)
]