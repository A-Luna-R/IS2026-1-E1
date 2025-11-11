from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class Song (models.Model):
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name='songs')
    title = models.CharField(max_length= 200)
    artist = models.CharField(max_length= 200, blank=True)  # opcional
    audio = models.FileField(upload_to= 'songs/%Y/%m/')      # se guarda en MEDIA_ROOT/songs/...
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

class UserSongLike(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='song_likes')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='liked_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.user.username} ❤️ {self.song.title}"

