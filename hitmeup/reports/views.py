from django.shortcuts import render

# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import datetime

from django.contrib.auth.models import User
from artists.models import Artist, ArtistSongLike
from songs.models import Song
from playlists.models import Playlist, PlaylistSong

def _parse_dates(request):
    today = timezone.localdate()
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    if start_str:
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
    else:
        start = today.replace(day= max(1, today.day - 30))  #  ~últimos ~30 días
    end = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else today

    start_dt = timezone.make_aware(datetime.combine(start, datetime.min.time()))
    end_dt = timezone.make_aware(datetime.combine(end, datetime.max.time()))
    return start, end, start_dt, end_dt

@staff_member_required
def dashboard(request):
    start, end, start_dt, end_dt = _parse_dates(request)

    totals = {
        'users': User.objects.count(),
        'artists': Artist.objects.count(),
        'songs': Song.objects.count(),
        'playlists': Playlist.objects.count(),
        'playlists_public': Playlist.objects.filter(is_public=True).count(),
        'likes': ArtistSongLike.objects.count(),
    }

    # En rango de fechas
    songs_in_range = Song.objects.filter(created_at__range=(start_dt, end_dt))
    playlists_in_range = Playlist.objects.filter(created_at__range=(start_dt, end_dt))
    likes_in_range = ArtistSongLike.objects.filter(created_at__range=(start_dt, end_dt))

    songs_by_day = (
        songs_in_range.annotate(day=TruncDate('created_at'))
        .values('day').annotate(count=Count('id')).order_by('day')
    )
    playlists_by_day = (
        playlists_in_range.annotate(day=TruncDate('created_at'))
        .values('day').annotate(count=Count('id')).order_by('day')
    )
    likes_by_day = (
        likes_in_range.annotate(day=TruncDate('created_at'))
        .values('day').annotate(count=Count('id')).order_by('day')
    )

    top_songs = (
        PlaylistSong.objects
        .values('song__id', 'song__title')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:10]
    )

    top_playlists = (
        PlaylistSong.objects
        .values('playlist__id', 'playlist__name')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:10]
    )

    ctx = {
        'start': start,
        'end': end,
        'totals': totals,
        'songs_by_day': list(songs_by_day),
        'playlists_by_day': list(playlists_by_day),
        'likes_by_day': list(likes_by_day),
        'top_songs': list(top_songs),
        'top_playlists': list(top_playlists),
    }
    return render(request, 'reports/dashboard.html', ctx)

# CSV

def _csv_response(name: str) -> HttpResponse:
    resp = HttpResponse(content_type= 'text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{name}"'
    return resp

def export_csv_summary(request):
    start, end, start_dt, end_dt = _parse_dates(request)
    resp = _csv_response(f"summary_{start}_to_{end}.csv")
    lines = []

    users = User.objects.count()
    artists = Artist.objects.count()
    songs = Song.objects.count()
    playlists = Playlist.objects.count()
    playlists_public = Playlist.objects.filter(is_public= True).count()
    likes = ArtistSongLike.objects.count()

    lines.append("metric,value\n")
    lines.append(f"users,{users}\n")
    lines.append(f"artists,{artists}\n")
    lines.append(f"songs,{songs}\n")
    lines.append(f"playlists,{playlists}\n")
    lines.append(f"playlists_public,{playlists_public}\n")
    lines.append(f"likes,{likes}\n")

    resp.write("".join(lines))
    return resp

def export_csv_songs(request):
    start, end, start_dt, end_dt = _parse_dates(request)
    resp = _csv_response(f"songs_{start}_to_{end}.csv")
    qs = (Song.objects
          .filter(created_at__range=(start_dt, end_dt))
          .values('id', 'title', 'artist', 'owner__username', 'created_at')
          .order_by('-created_at'))
    resp.write("id,title,artist,owner,created_at\n")
    for r in qs:
        title = (r['title'] or '').replace(',', ' ')
        artist = (r['artist'] or '').replace(',', ' ')
        owner = (r['owner__username'] or '').replace(',', ' ')
        resp.write(f"{r['id']},{title},{artist},{owner},{r['created_at']:%Y-%m-%d %H:%M:%S}\n")
    return resp

def export_csv_playlists(request):
    start, end, start_dt, end_dt = _parse_dates(request)
    resp = _csv_response(f"playlists_{start}_to_{end}.csv")
    qs = (Playlist.objects
          .filter(created_at__range=(start_dt, end_dt))
          .values('id', 'name', 'is_public', 'owner_user__username', 'owner_artist__stage_name', 'created_at')
          .order_by('-created_at'))
    resp.write("id,name,is_public,owner_user,owner_artist,created_at\n")
    for r in qs:
        name = (r['name'] or '').replace(',', ' ')
        owner_u = (r['owner_user__username'] or '')
        owner_a = (r['owner_artist__stage_name'] or '')
        resp.write(f"{r['id']},{name},{int(r['is_public'])},{owner_u},{owner_a},{r['created_at']:%Y-%m-%d %H:%M:%S}\n")
    return resp

def export_csv_likes(request):
    start, end, start_dt, end_dt = _parse_dates(request)
    resp = _csv_response(f"likes_{start}_to_{end}.csv")
    qs = (ArtistSongLike.objects
          .filter(created_at__range=(start_dt, end_dt))
          .values('id', 'artist__stage_name', 'song__title', 'created_at')
          .order_by('-created_at'))
    resp.write("id,artist,song,created_at\n")
    for r in qs:
        artist = (r['artist__stage_name'] or '').replace(',', ' ')
        song = (r['song__title'] or '').replace(',', ' ')
        resp.write(f"{r['id']},{artist},{song},{r['created_at']:%Y-%m-%d %H:%M:%S}\n")
    return resp

