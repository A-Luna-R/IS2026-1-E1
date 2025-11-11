from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name ='notifications_list'),
    path('read/<int:notif_id>', views.mark_read, name='notifications_mark_read'),
    path('read/all', views.mark_all_read, name='notifications_mark_all'),
]
