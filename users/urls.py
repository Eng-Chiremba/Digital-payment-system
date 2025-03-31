from django.urls import path, include
from . import views
from .views import LoginView
app_name='users'
urlpatterns = [
  path("landing/", views.landing, name='landing'),
  path("login/", LoginView.as_view(template_name='users/login.html'), name='login',),
  path("customer_signup/", views.customer_signup, name='register'),
  path("complete_profile", views.complete_profile, name='register'),
  path("business_signup/", views.business_signup, name='register'),

]


''' '''