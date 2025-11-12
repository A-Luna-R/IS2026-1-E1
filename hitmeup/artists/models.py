from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User  # Artista tmb inicia sesión
from songs.models import Song

class Artist(models.Model):
    account = models.OneToOneField(User, null= True, blank= True, on_delete=models.SET_NULL, related_name='artist_profile')
    name = models.CharField(max_length= 200, unique= True)
    bio = models.TextField(blank= True)
    is_public = models.BooleanField(default= True)

    def __str__(self):
        return self.name

class ArtistSongLike(models.Model):
    artist = models.ForeignKey(Artist, on_delete= models.CASCADE, related_name='likes')
    song = models.ForeignKey(Song, on_delete= models.CASCADE, related_name='liked_by_artists')
    created_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together = ('artist', 'song')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.artist.name} ❤️ {self.song.title}"

