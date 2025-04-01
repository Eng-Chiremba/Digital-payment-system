
from django.urls import path
from . import views


urlpatterns = [
  path('', views.home, name='home'),
  path('card/', views.cards, name='card'),
  path('payments/', views.payment, name='payments'),
  path('about/', views.about, name='about'),
  path('help', views.help, name='help'),
]
