from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from songs.models import Song

class Playlist(models.Model):
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name='playlists')
    name = models.CharField(max_length= 200)
    description = models.TextField(blank= True)
    songs = models.ManyToManyField(Song, through= 'PlaylistSong', related_name='in_playlists')
    created_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together = ('owner', 'name')  # cada usuario no repite nombre de playlist
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete= models.CASCADE)
    song = models.ForeignKey(Song, on_delete= models.CASCADE)
    added_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together = ('playlist', 'song')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.playlist.name} → {self.song.title}"
