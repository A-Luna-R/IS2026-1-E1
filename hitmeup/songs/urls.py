from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload_song, name= 'songs_upload'),
    path('list', views.songs_list, name= 'songs_list'),
    path('delete/<int:song_id>', views.delete_song, name= 'songs_delete'),
]