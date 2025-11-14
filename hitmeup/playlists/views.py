from django.shortcuts import render
from django.db.models import Q

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Playlist, PlaylistSong, UserPlaylistLike, ArtistPlaylistLike
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from .utils import sync_music_that_i_love
from artists.models import Artist
from django.shortcuts import redirect
from django.contrib import messages
from .forms import PlaylistCreateForm
from songs.models import Song
from django.db import transaction
from notifications.utils import notify


def playlists_list(request):
    lists_ = Playlist.objects.filter(owner=request.user)

    liked_user_ids = set()
    liked_artist_ids = set()
    artist_profile = None

    if request.user.is_authenticated:
        liked_user_ids = set(
            UserPlaylistLike.objects.filter(
                user=request.user,
                playlist__in=lists_
            ).values_list('playlist_id', flat=True)
        )

        artist_profile = getattr(request.user, 'artist_profile', None)

        if artist_profile:
            liked_artist_ids = set(
                ArtistPlaylistLike.objects.filter(
                    artist=artist_profile,
                    playlist__in=lists_
                ).values_list('playlist_id', flat=True)
            )

    return render(request, 'playlists/list.html', {
        'playlists': lists_,
        'liked_user_ids': liked_user_ids,
        'liked_artist_ids': liked_artist_ids,
        'has_artist': bool(artist_profile),
    })

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

def _is_owner(request, pl: Playlist) -> bool:
    if pl.owner_user and pl.owner_user_id == request.user.id:
        return True
    artist_profile = getattr(request.user, 'artist_profile', None)
    if pl.owner_artist and artist_profile and pl.owner_artist_id == artist_profile.id:
        return True
    return False

def delete_playlist_user(request, playlist_id: int):
    pl = get_object_or_404(Playlist, id=playlist_id, owner_user__isnull=False)
    if not _is_owner(request, pl) or pl.owner_user_id != request.user.id:
        return HttpResponseForbidden("No autorizado.")

    if request.method == 'POST':
        with transaction.atomic():
            name = pl.name
            pl.delete()
        messages.success(request, f'Playlist "{name}" eliminada.')
        return redirect('playlists_list')

    return render(request, 'playlists/delete_confirm.html', {'playlist': pl, 'owner_kind': 'user'})

def delete_playlist_artist(request, playlist_id: int):
    pl = get_object_or_404(Playlist, id=playlist_id, owner_artist__isnull=False)
    if not _is_owner(request, pl):
        return HttpResponseForbidden("No autorizado.")

    if request.method == 'POST':
        with transaction.atomic():
            name = pl.name
            pl.delete()
        messages.success(request, f'Playlist (artista) "{name}" eliminada.')
        return redirect('playlists_list')

    return render(request, 'playlists/delete_confirm.html', {'playlist': pl, 'owner_kind': 'artist'})
    
def _can_view_or_like_playlist(request, pl: Playlist) -> bool:
    if pl.is_public:
        return True
    if pl.owner_user and pl.owner_user_id == request.user.id:
        return True
    artist_profile = getattr(request.user, 'artist_profile', None)
    if pl.owner_artist and artist_profile and pl.owner_artist_id == artist_profile.id:
        return True
    return False

def playlist_toggle_like_user(request, playlist_id: int):
    pl = get_object_or_404(Playlist, id=playlist_id)
    if not _can_view_or_like_playlist(request, pl):
        return HttpResponseForbidden("No autorizado.")
    like, created = UserPlaylistLike.objects.get_or_create(user=request.user, playlist=pl)
    if created:
        try:
            if pl.owner_user:
                notify(recipient_user=pl.owner_user, actor=request.user,
                       verb="dio like a tu playlist", target=pl)
            elif pl.owner_artist:
                notify(recipient_artist=pl.owner_artist, actor=request.user,
                       verb="dio like a tu playlist", target=pl)
        except Exception:
            pass
        messages.success(request, "Te gustó la playlist (usuario).")
    else:
        like.delete()
        messages.info(request, "Quitaste el like (usuario).")
    return redirect(request.META.get('HTTP_REFERER', 'playlists_list'))

def playlist_toggle_like_artist(request, playlist_id: int):
    pl = get_object_or_404(Playlist, id=playlist_id)
    artist_profile = getattr(request.user, 'artist_profile', None)
    if not artist_profile:
        return HttpResponseForbidden("Tu cuenta no está asociada a un artista.")
    if not _can_view_or_like_playlist(request, pl):
        return HttpResponseForbidden("No autorizado.")
    like, created = ArtistPlaylistLike.objects.get_or_create(artist=artist_profile, playlist=pl)
    if created:
        try:
            if pl.owner_user:
                notify(recipient_user=pl.owner_user, actor=artist_profile,
                       verb="(artista) dio like a tu playlist", target=pl)
            elif pl.owner_artist:
                notify(recipient_artist=pl.owner_artist, actor=artist_profile,
                       verb="(artista) dio like a tu playlist", target=pl)
        except Exception:
            pass
        messages.success(request, "Te gustó la playlist (artista).")
    else:
        like.delete()
        messages.info(request, "Quitaste el like (artista).")
    return redirect(request.META.get('HTTP_REFERER', 'playlists_list'))

def playlists_liked(request):
    liked_as_user = Playlist.objects.filter(liked_by_users__user=request.user).order_by('-liked_by_users__created_at')
    artist_profile = getattr(request.user, 'artist_profile', None)
    liked_as_artist = Playlist.objects.none()
    if artist_profile:
        liked_as_artist = Playlist.objects.filter(liked_by_artists__artist=artist_profile).order_by('-liked_by_artists__created_at')
    return render(request, 'playlists/liked.html', {
        'liked_as_user': liked_as_user,
        'liked_as_artist': liked_as_artist,
        'has_artist': bool(artist_profile),
    })

