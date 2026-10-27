from django.urls import path
from . import views

urlpatterns = [
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/hire/<int:worker_pk>/', views.request_hire, name='request_hire'),
    path('jobs/<int:pk>/respond/', views.respond_job, name='respond_job'),
]