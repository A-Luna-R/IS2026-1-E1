from django import forms
from songs.models import Song

class PlaylistCreateForm(forms.Form):
    name = forms.CharField(max_length=200, label= "Nombre")
    description = forms.CharField(label="Descripción", required=False, widget=forms.Textarea)
    is_public = forms.BooleanField(label="Pública", required=False)

    songs = forms.ModelMultipleChoiceField(
        label="Canciones (opcional)",
        queryset=Song.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
