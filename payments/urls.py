from django.urls import path

from . import views

urlpatterns = [
    path('payments/checkout/<int:job_id>/', views.checkout, name='checkout'),
    path('payments/gateway/<int:txn_id>/', views.mock_gateway, name='mock_gateway'),
]