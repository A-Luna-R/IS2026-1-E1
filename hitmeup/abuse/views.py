from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

from songs.models import Song
from artists.models import Artist
from .models import SongReport
from .forms import SongReportForm

try:
    from notifications.utils import notify
except Exception:
    notify = None

def _as_artist_profile(user) -> Artist | None:
    return getattr(user, 'artist_profile', None)

def report_song(request, song_id: int):
    song = get_object_or_404(Song, id=song_id)
    if hasattr(song, 'owner') and song.owner_id == request.user.id:
        return HttpResponseForbidden("No puedes reportar tu propia canción.")

    if request.method == 'POST':
        form = SongReportForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.song = song
            artist = _as_artist_profile(request.user)
            if artist:
                r.reporter_artist = artist
            else:
                r.reporter_user = request.user
            r.save()
            messages.success(request, "Reporte enviado. Gracias por tu ayuda.")
            if notify and song.owner and song.owner != request.user:
                try:
                    notify(recipient_user=song.owner, actor=request.user,
                           verb="reportó tu canción", target=song,
                           message=f"Motivo: {r.get_reason_display()}")
                except Exception:
                    pass
            return redirect('song_detail', song_id=song.id)
    else:
        form = SongReportForm()
    return render(request, 'abuse/report_form.html', {'form': form, 'song': song})

def my_song_reports(request):
    qs = SongReport.objects.none()
    qs_user = SongReport.objects.filter(reporter_user=request.user)
    qs = qs.union(qs_user)
    artist = _as_artist_profile(request.user)
    if artist:
        qs = qs.union(SongReport.objects.filter(reporter_artist=artist))
    qs = qs.select_related('song').order_by('-created_at')

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'abuse/my_reports.html', {'page_obj': page_obj})

# Admin
def review_list(request):

    status = (request.GET.get('status') or 'open').lower()
    valid = {'open','review','resolved','rejected'}
    if status not in valid:
        status = 'open'
    qs = SongReport.objects.filter(status=status).select_related('song','reporter_user','reporter_artist')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'abuse/review_list.html', {'page_obj': page_obj, 'status': status})

def review_detail(request, report_id: int):
    r = get_object_or_404(SongReport.objects.select_related('song'), id=report_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = (request.POST.get('resolution_notes') or '').strip()
        if new_status not in dict(SongReport.STATUS_CHOICES):
            messages.error(request, "Estado inválido.")
        else:
            r.status = new_status
            r.resolution_notes = notes
            if new_status in ('resolved','rejected'):
                r.resolved_at = timezone.now()
                r.resolved_by = request.user
            r.save()
            messages.success(request, "Reporte actualizado.")

        return redirect('abuse_review_detail', report_id=r.id)

    return render(request, 'abuse/review_detail.html', {'r': r, 'STATUS_CHOICES': SongReport.STATUS_CHOICES})

