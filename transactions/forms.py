from django import forms
from .models import Transactions
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class TransactionForm(forms.ModelForm):
    amount = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Amount',
            'step': '0.01'
        })
    )
    
    customer_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Customer Name'
        })
    )
    
    customer_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'customer@example.com'
        })
    )
    
    customer_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction description',
            'rows': 3
        })
    )
    
    reference = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reference (Invoice number, etc.)'
        })
    )
    
    currency = forms.ChoiceField(
        choices=[
            ('USD', 'US Dollar'),
            ('ZWL', 'ZIG'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Transactions
        fields = [
            'amount', 'currency', 'customer_name', 'customer_email', 
            'customer_phone', 'description', 'reference'
        ]
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount


#this one is forr the creating the payment request by the provider
# forms.py


class Payment_Form(forms.ModelForm):
    # Override expires_at to use a date field in the form
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Transactions
        fields = ['description', 'amount', 'customer_email', 'expiry_date']
    
    def clean_expiry_date(self):
        """Ensure expiry date is in the future"""
        date = self.cleaned_data['expiry_date']
        if date < timezone.now().date():
            raise forms.ValidationError("Expiry date must be in the future")
        return date
    
    def save(self, commit=True):
        """Override save to convert date to datetime for expires_at"""
        instance = super().save(commit=False)
        
        # Convert the expiry_date to datetime for expires_at
        # Set it to end of day on the expiry date
        expiry_date = self.cleaned_data['expiry_date']
        instance.expires_at = timezone.make_aware(
            timezone.datetime.combine(
                expiry_date, 
                timezone.datetime.max.time()
            )
        )
        
        if commit:
            instance.save()
        return instance