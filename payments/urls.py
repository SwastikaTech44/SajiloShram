from django.urls import path

from . import views

urlpatterns = [
    path('payments/checkout/<int:job_id>/', views.checkout, name='checkout'),
    path('payments/gateway/<int:txn_id>/', views.mock_gateway, name='mock_gateway'),
    path('payments/esewa/pay/<int:txn_id>/', views.esewa_pay, name='esewa_pay'),
    path('payments/esewa/success/', views.esewa_success, name='esewa_success'),
    path('payments/esewa/failure/', views.esewa_failure, name='esewa_failure'),
]