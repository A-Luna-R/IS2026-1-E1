from django.db import models
from django.contrib.auth.models import User
from songs.models import Song
from artists.models import Artist

class Playlist(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete= models.CASCADE, related_name= 'playlists')
    name = models.CharField(max_length= 200, db_index=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

    songs = models.ManyToManyField(Song, through= 'PlaylistSong', related_name='in_playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        owner = self.owner.username
        return f"{self.name} [{owner}]"

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete= models.CASCADE)
    song = models.ForeignKey(Song, on_delete= models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'song')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.playlist.name} → {self.song.title}"
