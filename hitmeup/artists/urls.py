from django.urls import path
from . import views

urlpatterns = [
    path('<int:artist_id>/like/<int:song_id>', views.toggle_like, name='artist_toggle_like'),
]
