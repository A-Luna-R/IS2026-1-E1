from django.urls import path
from . import views

urlpatterns = [
    path('list', views.playlists_list, name= 'playlists_list'),
    path('<int:playlist_id>', views.playlist_detail, name= 'playlist_detail'),
    path('search', views.playlists_search, name= 'playlists_search'),
]

