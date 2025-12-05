from django.urls import path
from . import views

urlpatterns = [
    path('song/<int:song_id>/new', views.report_song, name= 'abuse_report_song'),
    path('mine', views.my_song_reports, name='abuse_my_reports'),

    path('review', views.review_list, name ='abuse_review_list'),
    path('review/<int:report_id>', views.review_detail, name='abuse_review_detail'),
]
