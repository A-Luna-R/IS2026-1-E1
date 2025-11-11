from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Playlist

def playlists_list(request):
    # Muestra SOLO las playlists del usuario actual
    lists_ = Playlist.objects.filter(owner= request.user)
    return render(request, 'playlists/list.html', {'playlists': lists_})

def playlist_detail(request, playlist_id):
    pl= get_object_or_404(Playlist, id= playlist_id, owner= request.user)

    songs = pl.songs.select_related('owner').all()
    return render(request, 'playlists/detail.html', {'playlist': pl, 'songs': songs})
