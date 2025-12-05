from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from artists.models import Artist

class Notification(models.Model):
    recipient_user   = models.ForeignKey(User,   null= True, blank= True, on_delete=models.CASCADE, related_name='notifications')
    recipient_artist = models.ForeignKey(Artist, null= True, blank=True, on_delete=models.CASCADE, related_name='notifications')

    actor_ct  = models.ForeignKey(ContentType, null= True, blank= True, on_delete=models.SET_NULL, related_name='+')
    actor_id  = models.PositiveIntegerField(null= True, blank= True)
    actor     = GenericForeignKey('actor_ct', 'actor_id')

    target_ct = models.ForeignKey(ContentType, null= True, blank= True, on_delete=models.SET_NULL, related_name='+')
    target_id = models.PositiveIntegerField(null= True, blank= True)
    target    = GenericForeignKey('target_ct', 'target_id')

    verb      = models.CharField(max_length= 120)
    message   = models.TextField(blank= True)
    is_read   = models.BooleanField(default= False)
    created_at= models.DateTimeField(default= timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.recipient_artist.stage_name if self.recipient_artist else (self.recipient_user.username if self.recipient_user else '—')
        return f"[{who}] {self.verb}"

