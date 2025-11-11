from django import forms
from .models import Song

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'audio']

    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if not audio:
            return audio
        # Validación simple de extensión
        valid_exts = ('.mp3', '.wav', '.m4a')
        name = audio.name.lower()
        if not any(name.endswith(ext) for ext in valid_exts):
            raise forms.ValidationError("Formato no válido. Usa mp3, wav o .m4a")
        return audio
