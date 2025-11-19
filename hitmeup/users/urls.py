"""
URL configuration for hitmeup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.urls import path
from .views import LandingView, RegisterView, Logout

urlpatterns = [
    path('', LandingView.as_view(), name= "landing"),
    path('register', RegisterView.as_view(), name= "register"), 
    path('logout', Logout.as_view(), name= "logout"),
    path('search', search_people, name='people_search'),
]
