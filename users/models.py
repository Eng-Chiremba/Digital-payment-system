from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('service_provider', 'Service Provider'),
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    
     # additional feilds for service provider
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    
    date_of_birth = models.DateField(null=True, blank=True)
    id_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username
