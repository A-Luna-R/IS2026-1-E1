from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Create your views here.

class LandingView(LoginView):
    template_name = 'users/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # o 'dashboard'
        return super().dispatch(request, *args, **kwargs)
    
<<<<<<< HEAD
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

def logout_confirm_view(request):
  return render(request, "users/logout_confirm.html")

def logout_view(request):
  logout(request)
  messages.success(request, "Has cerrado sesión correctamente.")
  return redirect("landing")
=======
class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = "home"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
class Logout(LogoutView):
    success_url = "landing"
>>>>>>> f492059 (fix(register): usuarios se registran correctamente; feat(logout) implementación del cierre de sesión)
