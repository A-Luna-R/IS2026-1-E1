from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SongForm
from .models import Song, UserSongLike
from notifications.utils import notify 

def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.owner = request.user
            song.save()
            messages.success(request, "Canción subida correctamente.")
            return redirect('songs_list')
    else:
        form = SongForm()
    return render(request, 'songs/upload.html', {'form': form})

def songs_list(request):
    songs = Song.objects.filter(owner=request.user).order_by('-created_at')
    liked_ids = set(UserSongLike.objects.filter(user=request.user, song__in=songs).values_list('song_id', flat= True))
    return render(request, 'songs/list.html', {'songs': songs, 'liked_ids': liked_ids})


def delete_song(request, song_id):
    song = get_object_or_404(Song, id= song_id, owner= request.user)
    if request.method == 'POST':
        song.delete()
        messages.success(request, "Canción eliminada.")
        return redirect('songs_list')
    return render(request, 'songs/delete_confirm.html', {'song': song})

def toggle_like_user(request, song_id: int):
    song = get_object_or_404(Song, id=song_id)
    like, created = UserSongLike.objects.get_or_create(user=request.user, song=song)
    if created:
        if hasattr(song, 'owner') and song.owner and song.owner != request.user:
            try:
                notify(
                    recipient_user=song.owner,
                    actor= request.user,
                    verb=" dio like a tu canción.",
                    target=song,
                    message=f"{request.user.username} marcó con ❤️ “{song.title}”."
                )
            except Exception:
                pass
        messages.success(request, "TLikeaste la canción.")
    else:
        like.delete()
        messages.info(request, "Quitaste el like.")
    return redirect(request.META.get('HTTP_REFERER', 'songs_list'))

def liked_songs(request):
    qs = (Song.objects
          .filter(liked_by_users__user=request.user)
          .select_related('owner')
          .order_by('-liked_by_users__created_at'))
    return render(request, 'songs/liked.html', {'songs': qs})
