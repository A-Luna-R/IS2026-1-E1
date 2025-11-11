from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import User
from .forms import RegisterForm

# Create your views here.

class LandingView(LoginView):
    template_name = 'users/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # o 'dashboard'
        return super().dispatch(request, *args, **kwargs)
    
def register_user(request): 
    if request.method == 'POST':
        form = RegisterForm(request.POST)   
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully created account")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})
