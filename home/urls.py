
from django.urls import path, include
from . import views


urlpatterns = [
  path('debug/users/', views.list_users),

  path('', views.landing, name='landing'),
  path("", include("users.urls")),
  path('costumer/', views.customer_dashboard, name='customer-dashboard'),
  path('payments/', views.payments, name='payments'),
  
  path('cards/', views.manage_cards, name='manage_cards'),
  path('cards/add/', views.add_card, name='add_card'),
  path('transactions/', views.customer_transaction_history, name='customer_transaction_history'),
  path('credit-score/', views.credit_score, name='credit_score'),
  path('signout/', views.signout, name='signout'),
  path('api/get-payment-details/<str:payment_id>/', views.get_payment_details, name='get_payment_details'),
  path('api/process-payment/', views.process_payment, name='process_payment'),

#service provider
  path('business/', views.provider_dashboard, name='provider-dashboard'),
  path('business/settings', views.account_settings, name='provider-settings'),
  path('business/create-payment/', views.create_payment, name='create_payment'),
  path('transactions/', views.provider_transaction_history, name='provider_transaction_history'),
  path('profile/update/', views.update_profile, name='update_profile'),
  path('bank-accounts/api/', views.bank_accounts_api, name='bank_accounts_api'),
  path('bank-accounts/add/', views.add_bank_account, name='add_bank_account'),
  path('bank-accounts/<int:account_id>/', views.get_bank_account, name='get_bank_account'),
  path('business-profile/update/', views.update_business_profile, name='update_business_profile'),
  path('verification/upload/', views.upload_verification_document, name='upload_verification_document'),
  path('security/update/', views.update_security_settings, name='update_security_settings'),
  path('notifications/update/', views.update_notification_preferences, name='update_notification_preferences'),
]

