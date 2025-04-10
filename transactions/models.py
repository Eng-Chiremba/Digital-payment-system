from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import random
import string
from home.models import PaymentMethod


class PaymentMethod(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    code = models.CharField(_("Code"), max_length=20, unique=True)
    icon = models.ImageField(_("Icon"), upload_to='payment_methods/', blank=True, null=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    processing_fee_percentage = models.DecimalField(_("Processing Fee (%)"), max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name


class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    COMPLETED = 'COMPLETED', _('Completed')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Refunded')
    CANCELLED = 'CANCELLED', _('Cancelled')


class Transactions(models.Model):
    # Transaction identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.CharField(_("Payment ID"), max_length=50, unique=True, blank=True)
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    # Amount information
    amount = models.DecimalField(_("Amount"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default="USD")
    processing_fee = models.DecimalField(_("Processing Fee"), max_digits=10, decimal_places=2, default=0)
    
    # User information
    service_provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="provider_transactions"
    )
    customer_email = models.EmailField(_("Customer Email"), blank=True, null=True)
    customer_phone = models.CharField(_("Customer Phone"), max_length=20, blank=True, null=True)
    customer_name = models.CharField(_("Customer Name"), max_length=100, blank=True, null=True)
    
    # Payment information
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="transactions"
    )
    status = models.CharField(
        _("Status"), 
        max_length=20, 
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )
    
    # Transaction details
    description = models.TextField(_("Description"), blank=True)
    items = models.JSONField(_("Items"), default=dict, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    expires_at = models.DateTimeField(_("Expires At"), blank=True, null=True)
    completed_at = models.DateTimeField(_("Completed At"), blank=True, null=True)
    
    # Response from payment gateway
    gateway_response = models.JSONField(_("Gateway Response"), blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Generate payment_id if it doesn't exist
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        return self.amount + self.processing_fee
    
    @property
    def formatted_amount(self):
        """Return amount formatted as currency string for the form response"""
        return f"${self.amount:.2f}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def calculate_processing_fee(self):
        if not self.payment_method:
            return 0
        
        fee_percentage = self.payment_method.processing_fee_percentage
        return (self.amount * fee_percentage) / 100
    
    @classmethod
    def generate_payment_id(cls):
        """Generate a unique payment ID"""
        prefix = "TXN-"
        # Generate a random string of 5 characters (mix of letters and numbers)
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        payment_id = f"{prefix}{random_part}"
        
        # Ensure it's unique
        while cls.objects.filter(payment_id=payment_id).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            payment_id = f"{prefix}{random_part}"
            
        return payment_id


class TransactionHistory(models.Model):
    transaction = models.ForeignKey(
        Transactions, 
        on_delete=models.CASCADE, 
        related_name="history"
    )
    status = models.CharField(_("Status"), max_length=20, choices=TransactionStatus.choices)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Transaction Histories"
    
    def __str__(self):
        return f"{self.transaction.payment_id} - {self.status} at {self.timestamp}"