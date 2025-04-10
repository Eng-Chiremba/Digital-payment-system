from django.db import models
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class PaymentMethod(models.Model):
    
    PAYMENT_TYPE_CHOICES = [
        ('bank', 'Bank'),
        ('mobile_wallet', 'Mobile Wallet'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]
    CARD_TYPE =[
        ('ecocash', 'EcoCash'),
        ('CBZ bank', 'cbz bank'),
        ('NMB Bank', 'nmb bank'),
        ('visa', 'visa'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    card_type = models.CharField(max_length=100, choices=CARD_TYPE, default='EcoCash')  # e.g., 'Ecocash', 'CBZ bank'
    card_number = models.CharField(max_length=50)  
    type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='bank')
    is_default = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.card_type} - {self.card_number}"
    
    def save(self, *args, **kwargs):
        
        if self.is_default:
       
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Transaction(models.Model):
    """Model for storing transaction records"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    transaction_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(default=timezone.now)
    merchant = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.merchant} - {self.amount}"
    
    class Meta:
        ordering = ['-date']  # Most recent transactions first

class CreditScore(models.Model):
    """Model for storing user credit score information"""
    CATEGORY_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Poor', 'Poor'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_score')
    score = models.IntegerField()
    max_score = models.IntegerField(default=850)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    last_updated = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.max_score} - {self.category}"

class CreditFactor(models.Model):
    """Model for storing factors that affect credit score"""
    IMPACT_CHOICES = [
        ('Positive', 'Positive'),
        ('Neutral', 'Neutral'),
        ('Negative', 'Negative'),
    ]
    
    credit_score = models.ForeignKey(CreditScore, on_delete=models.CASCADE, related_name='factors')
    title = models.CharField(max_length=100)
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.title} - {self.impact}"

class PaymentRequest(models.Model):
    """Model for storing payment requests"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Expired', 'Expired'),
        ('Cancelled', 'Cancelled'),
    ]
    
    payment_id = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(default=timezone.now)
    merchant = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.payment_id} - {self.merchant} - {self.amount}"
    
class PaymentCategory(models.Model):
    """Model for payment categories  (ZESA, Airtime, Insurance,)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, help_text="Icon class name", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Payment Categories"

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20, 
        choices=[('verified', 'Verified'), ('pending', 'Pending'), ('unverified', 'Unverified')],
        default='unverified'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings Account'),
        ('current', 'Current Account'),
        ('business', 'Business Account'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    branch_code = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number[-4:]}"
    
    def save(self, *args, **kwargs):
        # If this is marked as primary, ensure no other account for this user is primary
        if self.is_primary:
            BankAccount.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        
        # If this is the only account, make it primary
        if not self.pk and not BankAccount.objects.filter(user=self.user).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)
    
    def get_masked_account_number(self):
        """Return account number with only last 4 digits visible"""
        if len(self.account_number) <= 4:
            return self.account_number
        return '•' * (len(self.account_number) - 4) + self.account_number[-4:]

class BusinessProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business')

    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.business_name

class VerificationDocument(models.Model):
    DOCUMENT_TYPES = [
        ('id', 'National ID'),
        ('passport', 'Passport'),
        ('driver_license', 'Driver\'s License'),
        ('business_reg', 'Business Registration'),
        ('tax_clearance', 'Tax Clearance'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='verification_docs/')
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user.username}"