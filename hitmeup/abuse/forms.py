from django import forms
from .models import SongReport

class SongReportForm(forms.ModelForm):
    class Meta:
        model = SongReport
        fields = ['reason', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4, 'placeholder': '¿Cuál es el probelma? (máx. 1,000 caracteres).'}),
        }

    def clean_details(self):
        txt = (self.cleaned_data.get('details') or '').strip()
        if len(txt) > 1000:
            raise forms.ValidationError("Máximo 1000 caracteres.")
        return txt
