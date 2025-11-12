from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Playlist
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from .utils import sync_music_that_i_love
from artists.models import Artist

def playlists_list(request):
    lists_ = Playlist.objects.filter(owner= request.user)
    return render(request, 'playlists/list.html', {'playlists': lists_})

def playlist_detail(request, playlist_id):
    pl= get_object_or_404(Playlist, id= playlist_id, owner= request.user)

    songs = pl.songs.select_related('owner').all()
    return render(request, 'playlists/detail.html', {'playlist': pl, 'songs': songs})

def playlists_search(request):
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        results = (
            Playlist.objects
            .filter(owner= request.user)
            .filter(
                Q(name__icontains= q) |
                Q(description__icontains= q) |
                Q(songs__title__icontains= q)
            )
            .distinct()
            .order_by('name')
        )

    ctx = {
        'q': q,
        'results': results,
        'count': len(results) if q else 0,
    }
    return render(request, 'playlists/search.html', ctx)

def artist_love_playlist(request, artist_id: int):
    """
    Muestra la playlist pública 'Music That I Love' del artista.
    La sincroniza antes de mostrar.
    """
    # Control de acceso: público para ver, pero sincronizamos solo si es staff o el dueño
    pl = sync_music_that_i_love(artist_id)
    songs = pl.songs.select_related('owner').all()
    return render(request, 'playlists/artist_love.html', {'playlist': pl, 'songs': songs})

def artist_love_sync(request, artist_id: int):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")

    artist = Artist.objects.get(id= artist_id)
    is_owner_artist = (hasattr(request.user, 'artist_profile') and request.user.artist_profile.id == artist.id)
    if not (request.user.is_staff or is_owner_artist):
        return HttpResponseForbidden("No autorizado")

    pl = sync_music_that_i_love(artist_id)
    messages.success(request, f"Playlist '{pl.name}' sincronizada.")
    return redirect('playlist_artist_love', artist_id= artist_id)

