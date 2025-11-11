from django.shortcuts import render

# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SongForm
from .models import Song

def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.owner = request.user
            song.save()
            messages.success(request, "Canción subida correctamente.")
            return redirect('songs-list')
    else:
        form = SongForm()
    return render(request, 'songs/upload.html', {'form': form})

def songs_list(request):
    # Lista solo las del usuario actual; cambia a Song.objects.all() si quieres global
    songs = Song.objects.filter(owner= request.user).order_by('-created_at')
    return render(request, 'songs/list.html', {'songs': songs})

def delete_song(request, song_id):
    song = get_object_or_404(Song, id= song_id, owner= request.user)
    if request.method == 'POST':
        song.delete()
        messages.success(request, "Canción eliminada.")
        return redirect('songs_list')
    return render(request, 'songs/delete_confirm.html', {'song': song})
