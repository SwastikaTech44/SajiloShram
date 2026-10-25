from django.urls import path
from . import views

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/<int:profile_id>/', views.worker_detail, name='worker_detail'),
]