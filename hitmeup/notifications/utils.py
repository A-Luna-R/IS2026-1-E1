from django.contrib.contenttypes.models import ContentType
from .models import Notification

def notify(*, recipient_user=None, recipient_artist=None, actor=None, verb:str, target= None, message:str= ""):
    assert (recipient_user is None) ^ (recipient_artist is None), "Debe haber exactamente un tipo de receptor"
    n = Notification(recipient_user=recipient_user, recipient_artist=recipient_artist, verb=verb, message=message)
    if actor is not None:
        n.actor_ct = ContentType.objects.get_for_model(actor.__class__)
        n.actor_id = actor.id
    if target is not None:
        n.target_ct = ContentType.objects.get_for_model(target.__class__)
        n.target_id = target.id
    n.save()
    return n
