from django.urls import path
from . import views

urlpatterns = [
    path('list-playlists', views.playlists_list, name= 'list-playlists'),
    path('<int:playlist_id>', views.playlist_detail, name= 'playlist'),
    path('search-lists', views.playlists_search, name= 'search-lists'),
]

