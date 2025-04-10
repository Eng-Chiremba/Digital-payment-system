from django import forms
from .models import PaymentMethod, Transaction

class PaymentMethodForm(forms.ModelForm):
    """Form for adding or editing payment methods"""
    class Meta:
        model = PaymentMethod
        fields = ['card_type', 'card_number', 'type', 'is_default']
        widgets = {
            'card_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Ecocash, CBZ Bank'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter card number or mobile number'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'card_type': 'Payment Method Name',
            'card_number': 'Card/Mobile Number',
            'type': 'Payment Type',
            'is_default': 'Set as Default Payment Method',
        }

class PaymentForm(forms.Form):
    """Form for making payments"""
    payment_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TXN-12345'}),
        required=True,
        help_text='Enter the payment ID received from the merchant'
    )
    
class PaymentMethodSelectionForm(forms.Form):
    """Form for selecting payment method during checkout"""
    payment_method = forms.Model