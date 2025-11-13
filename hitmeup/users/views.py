from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from artists.models import Artist

# Create your views here.

class LandingView(LoginView):
    template_name = 'users/landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # o 'dashboard'
        return super().dispatch(request, *args, **kwargs)
    
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

def search_people(request):
q = (request.GET.get('q') or '').strip()
    kind = (request.GET.get('type') or 'all').strip().lower()
    kind = kind if kind in ('users', 'artists', 'all') else 'all'

    items = []
    if q:
        if kind in ('all', 'users'):
            qs_users = (
                User.objects
                .filter(
                    Q(username__icontains=q) |
                    Q(first_name__icontains=q) |
                    Q(last_name__icontains=q)
                )
                .order_by('username')[:200]
            )
            for u in qs_users:
                subtitle = " ".join([u.first_name or "", u.last_name or ""]).strip()
                items.append({
                    'type': 'user',
                    'id': u.id,
                    'title': u.username,
                    'subtitle': subtitle,
                })

        if kind in ('all', 'artists'):
            qs_artists = (
                Artist.objects
                .filter(
                    Q(stage_name__icontains=q) |
                    Q(bio__icontains=q)
                )
                .order_by('stage_name')[:200]
            )
            for a in qs_artists:
                items.append({
                    'type': 'artist',
                    'id': a.id,
                    'title': a.stage_name,
                    'subtitle': 'Artista',
                })

    paginator = Paginator(items, 20)  # 20 resultados por página (combinados)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    ctx = {
        'q': q,
        'type': kind,
        'page_obj': page_obj,
    }
    return render(request, 'users/search_people.html', ctx)

