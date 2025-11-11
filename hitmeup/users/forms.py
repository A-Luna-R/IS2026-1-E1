from django import forms
from django.core.exceptions import ValidationError
from .models import User

class RegisterForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            "password" : forms.PasswordInput(),
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.data.get('confirm_password')   
        if password != confirm_password:
            raise ValidationError("Passwords do not match")
        return password