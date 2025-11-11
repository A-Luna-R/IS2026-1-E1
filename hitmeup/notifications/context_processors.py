from .models import Notification

def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    user = request.user
    artist = getattr(user, 'artist_profile', None)

    user_count = Notification.objects.filter(recipient_user =user, is_read=False).count()
    artist_count = Notification.objects.filter(recipient_artist=artist, is_read=False).count() if artist else 0
    return {'unread_notifications_count': user_count + artist_count}
