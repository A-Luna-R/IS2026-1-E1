from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SongForm
from .models import Song, UserSongLike
from notifications.utils import notify
from django.db.models import Q, Count
from django.core.paginator import Paginator
from artists.models import ArtistSongLike

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
        messages.success(request, "Likeaste la canción.")
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

def explore_songs(request):
    q = (request.GET.get('q') or '').strip()
    order = (request.GET.get('order') or 'newest').strip()

    songs = Song.objects.all().select_related('owner')

    if q:
        songs = songs.filter(
            Q(title__icontains=q) |
            Q(artist__icontains=q) |
            Q(owner__username__icontains=q)
        )

    songs = songs.annotate(
        likes_users=Count('liked_by_users', distinct=True),
        likes_artists=Count('liked_by_artists', distinct=True),
    )

    if order == 'title':
        songs = songs.order_by('title', '-created_at')
    elif order == 'most_liked':
        songs = songs.order_by('-likes_users', '-created_at')
    elif order == 'most_liked_artists':
        songs = songs.order_by('-likes_artists', '-created_at')
    else:  # newest
        songs = songs.order_by('-created_at')

    liked_user_ids = set(
        UserSongLike.objects
        .filter(user=request.user, song__in=songs)
        .values_list('song_id', flat=True)
    )

    artist_profile = getattr(request.user, 'artist_profile', None)
    liked_artist_ids = set()
    if artist_profile:
        liked_artist_ids = set(
            ArtistSongLike.objects
            .filter(artist=artist_profile, song__in=songs)
            .values_list('song_id', flat=True)
        )

    paginator = Paginator(songs, 12)  # 12 por página
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    ctx = {
        'page_obj': page_obj,
        'q': q,
        'order': order,
        'liked_user_ids': liked_user_ids,
        'liked_artist_ids': liked_artist_ids,
        'has_artist': bool(artist_profile),
    }
    return render(request, 'songs/explore.html', ctx)

def song_detail(request, song_id: int):
    s = get_object_or_404(Song.objects.select_related('owner'), id=song_id)
    liked_user = UserSongLike.objects.filter(user=request.user, song=s).exists()
    artist_profile = getattr(request.user, 'artist_profile', None)
    liked_artist = False
    if artist_profile:
        liked_artist = ArtistSongLike.objects.filter(artist=artist_profile, song=s).exists()

    counts = (
        Song.objects.filter(id=s.id)
        .annotate(
            likes_users=Count('liked_by_users', distinct=True),
            likes_artists=Count('liked_by_artists', distinct=True),
        )
        .values('likes_users', 'likes_artists')
        .first()
        or {'likes_users': 0, 'likes_artists': 0}
    )

    return render(request, 'songs/detail.html', {
        'song': s,
        'liked_user': liked_user,
        'liked_artist': liked_artist,
        'has_artist': bool(artist_profile),
        'likes_users': counts['likes_users'],
        'likes_artists': counts['likes_artists'],
    })

