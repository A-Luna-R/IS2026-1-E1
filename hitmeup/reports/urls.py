from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name= 'reports_dashboard'),
    path('export/csv/summary', views.export_csv_summary, name= 'reports_export_summary'),
    path('export/csv/songs', views.export_csv_songs, name= 'reports_export_songs'),
    path('export/csv/playlists', views.export_csv_playlists, name= 'reports_export_playlists'),
    path('export/csv/likes', views.export_csv_likes, name= 'reports_export_likes'),
]