from django.urls import path
from . import views

urlpatterns = [
    path('upload-song', views.upload_song, name= 'upload-song'),
    path('songs-list', views.songs_list, name= 'songs-list'),
    path('delete/<int:song_id>', views.delete_song, name= 'delete-song'),
]