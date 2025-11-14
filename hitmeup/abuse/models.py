from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from songs.models import Song
from artists.models import Artist

class SongReport(models.Model):
    REASON_CHOICES = [
        ('copyright', 'Infracción de derechos de autor'),
        ('offensive',  'Contenido ofensivo'),
        ('spam',       'Spam / contenido engañoso'),
        ('other',      'Otro'),
    ]
    STATUS_CHOICES = [
        ('open',        'Abierto'),
        ('review',      'En revisión'),
        ('resolved',    'Resuelto'),
        ('rejected',    'Rechazado'),
    ]

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='reports')
    reporter_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='song_reports')
    reporter_artist = models.ForeignKey(Artist, null=True, blank=True, on_delete=models.SET_NULL, related_name='song_reports')

    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(default=timezone.now)

    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='song_reports_resolved')
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        who = self.reporter_artist.stage_name if self.reporter_artist else (self.reporter_user.username if self.reporter_user else '—')
        return f"[{self.get_status_display()}] {self.song.title} ← {who}"

