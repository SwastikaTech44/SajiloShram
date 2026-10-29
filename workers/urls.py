from django.urls import path
from . import views

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<int:profile_id>/', views.worker_detail, name='worker_detail'),
    path('profile/record/', views.record_intro, name='record_intro'),
    path('profile/upload-audio/', views.upload_audio, name='upload_audio'),
    path('profile/verify-nid/', views.verify_nid, name='verify_nid'),
]