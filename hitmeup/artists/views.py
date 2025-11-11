from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from songs.models import Song
from .models import Artist, ArtistSongLike
from notifications.utils import notify

def toggle_like(request, song_id: int, artist_id: int):
    artist = get_object_or_404(Artist, id= artist_id)
    is_owner_artist = (hasattr(request.user, 'artist_profile') and request.user.artist_profile.id == artist.id)
    if not (request.user.is_staff or is_owner_artist):
        return HttpResponseForbidden("No autorizado.")

    song = get_object_or_404(Song, id= song_id)
    like, created = ArtistSongLike.objects.get_or_create(artist= artist, song=song)
    if not created:
        like.delete()
    else:
        # notificación al dueño de la canción (User)
        if hasattr(song, 'owner') and song.owner:
            try:
                notify(
                    recipient_user=song.owner,
                    actor=artist,
                    verb="(artista) dio like a tu canción",
                    target=song,
                    message=f"{artist.stage_name} marcó con ❤️ “{song.title}”."
                )
            except Exception:
                pass
    return redirect(request.META.get('HTTP_REFERER', 'songs_list'))
