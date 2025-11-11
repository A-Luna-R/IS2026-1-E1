from django.db import transaction
from .models import Playlist, PlaylistSong
from artists.models import Artist, ArtistSongLike

PLAYLIST_NAME = "Music That I Love"

def sync_music_that_i_love(artist_id: int) -> Playlist:
    artist = Artist.objects.get(id=artist_id)

    pl, _ = Playlist.objects.get_or_create(
        owner_artist= artist,
        name= PLAYLIST_NAME,
        defaults= {
            'description': 'Canciones que el artista ha marcado con ♥',
            'is_public': True,
        }
    )

    liked_song_ids = ArtistSongLike.objects.filter(artist= artist).values_list('song_id', flat= True)

    PlaylistSong.objects.filter(playlist= pl).exclude(song_id__in= liked_song_ids).delete()

    existing = set(PlaylistSong.objects.filter(playlist= pl).values_list('song_id', flat= True))
    to_add = [sid for sid in liked_song_ids if sid not in existing]
    PlaylistSong.objects.bulk_create([PlaylistSong(playlist= pl, song_id= sid) for sid in to_add])

    if not pl.is_public:
        pl.is_public = True
        pl.save(update_fields= ['is_public'])

    return pl
