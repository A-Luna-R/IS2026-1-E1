from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Playlist, PlaylistSong
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from .utils import sync_music_that_i_love
from artists.models import Artist
from django.shortcuts import redirect
from django.contrib import messages
from .forms import PlaylistCreateForm
from songs.models import Song

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

def create_playlist_user(request):
    if request.method == 'POST':
        form = PlaylistCreateForm(request.POST)
        form.fields['songs'].queryset = Song.objects.filter(owner=request.user).order_by('-created_at')
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            desc = form.cleaned_data['description']
            is_public = form.cleaned_data['is_public']
            songs = form.cleaned_data['songs']

            if Playlist.objects.filter(owner_user=request.user, name=name).exists():
                form.add_error('name', 'Ya tienes una playlist con ese nombre.')
            else:
                pl = Playlist.objects.create(
                    owner_user=request.user,
                    name=name,
                    description=desc,
                    is_public=is_public
                )
                if songs:
                    PlaylistSong.objects.bulk_create([PlaylistSong(playlist=pl, song=s) for s in songs])
                messages.success(request, "Playlist creada.")
                return redirect('playlist_detail', playlist_id=pl.id)
    else:
        form = PlaylistCreateForm()
        form.fields['songs'].queryset = Song.objects.filter(owner=request.user).order_by('-created_at')

    return render(request, 'playlists/new.html', {
        'form': form,
        'owner_kind': 'user',
    })

def create_playlist_artist(request):
    artist_profile = getattr(request.user, 'artist_profile', None)
    if not artist_profile:
        return HttpResponseForbidden("Tu cuenta no está asociada a un artista.")

    owner_user_for_songs = artist_profile.account or request.user

    if request.method == 'POST':
        form = PlaylistCreateForm(request.POST)
        form.fields['songs'].queryset = Song.objects.filter(owner=owner_user_for_songs).order_by('-created_at')
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            desc = form.cleaned_data['description']
            is_public = form.cleaned_data['is_public']
            songs = form.cleaned_data['songs']

            if Playlist.objects.filter(owner_artist=artist_profile, name=name).exists():
                form.add_error('name', 'Ese artista ya tiene una playlist con ese nombre.')
            else:
                pl = Playlist.objects.create(
                    owner_artist=artist_profile,
                    name=name,
                    description=desc,
                    is_public=is_public
                )
                if songs:
                    PlaylistSong.objects.bulk_create([PlaylistSong(playlist=pl, song=s) for s in songs])
                messages.success(request, "Playlist (artista) creada.")
                return redirect('playlist_detail', playlist_id=pl.id)
    else:
        form = PlaylistCreateForm()
        form.fields['songs'].queryset = Song.objects.filter(owner=owner_user_for_songs).order_by('-created_at')

    return render(request, 'playlists/new.html', {
        'form': form,
        'owner_kind': 'artist',
        'artist_profile': artist_profile,
    })
