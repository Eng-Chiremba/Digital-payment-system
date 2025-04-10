from django.urls import path
from . import views

urlpatterns = [
    # Service Provider URLs
    path('service-home', views.service_provider_dashboard, name='service_provider_dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    
    path('transactions/<str:payment_id>/', views.transaction_detail, name='transaction_detail'),
    
    # Customer URLs
    path('pay/', views.verify_payment, name='verify_payment'),
    path('pay/<str:payment_id>/', views.verify_payment, name='verify_payment_with_id'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-status/<str:payment_id>/', views.payment_status, name='payment_status'),
    
    # API URLs
    path('api/transaction-status/<str:payment_id>/', views.check_transaction_status, name='check_transaction_status'),
]
"""path('transactions/initiate/', views.initiate_transaction, name='initiate_transaction'),"""