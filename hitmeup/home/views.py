from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import TemplateView

# Create your views here.

class HomeView(TemplateView):
    template_name = 'home/home.html'
