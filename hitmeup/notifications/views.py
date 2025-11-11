from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Notification

def _user_artist_ids(request):
    user = request.user
    artist_id = getattr(getattr(user, 'artist_profile', None), 'id', None)
    return user.id, artist_id

def notifications_list(request):
    user_id, artist_id = _user_artist_ids(request)
    qs = Notification.objects.none()
    if user_id:
        qs = qs.union(Notification.objects.filter(recipient_user_id=user_id))
    if artist_id:
        qs = qs.union(Notification.objects.filter(recipient_artist_id=artist_id))
    qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'notifications/list.html', {'page_obj': page_obj})

def mark_read(request, notif_id: int):
    n = get_object_or_404(Notification, id= notif_id)
    user_id, artist_id = _user_artist_ids(request)
    # Autorizar solo si pertenece al receptor
    if not ((n.recipient_user_id and n.recipient_user_id == user_id) or (n.recipient_artist_id and n.recipient_artist_id == artist_id)):
        return HttpResponseForbidden("No autorizado")

    n.is_read = True
    n.save(update_fields=['is_read'])
    return redirect('notifications_list')

def mark_all_read(request):
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    user_id, artist_id = _user_artist_ids(request)
    if user_id:
        Notification.objects.filter(recipient_user_id= user_id, is_read=False).update(is_read=True)
    if artist_id:
        Notification.objects.filter(recipient_artist_id =artist_id, is_read=False).update(is_read=True)
    return redirect('notifications_list')

