from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from songs.models import Song
from .models import Artist, ArtistSongLike

def toggle_like(request, song_id: int, artist_id: int):
    artist = get_object_or_404(Artist, id=artist_id)
    is_owner_artist = (hasattr(request.user, 'artist_profile') and request.user.artist_profile.id == artist.id)
    if not (request.user.is_staff or is_owner_artist):
        return HttpResponseForbidden("No tienes acceso.")

    song = get_object_or_404(Song, id= song_id)
    like, created = ArtistSongLike.objects.get_or_create(artist= artist, song= song)
    if not created:
        like.delete()
    return redirect('playlist_liked_by_artist', artist_id= artist.id)

