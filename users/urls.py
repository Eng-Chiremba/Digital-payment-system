from django.urls import path
from . import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('customer/signup/', views.customer_signup, name='customer-signup'),
    path('business/signup/', views.business_signup, name='business-signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('complete-profile/', views.complete_profile, name='complete-profile'),
]
