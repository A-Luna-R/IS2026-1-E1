from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Playlist

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
            .filter(owner=request.user)
            .filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(songs__title__icontains=q)
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

