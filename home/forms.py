from django import forms
from .models import PaymentMethod, Transaction, Profile, BankAccount, BusinessProfile, VerificationDocument
from django.contrib.auth.models import User


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
    payment_method = forms.models

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'province', 'profile_picture']
        
    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError("Image file too large ( > 2MB )")
        return image

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_holder', 'account_number', 'account_type', 'branch_code', 'is_primary']
        
    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')

        if not account_number.isdigit():
            raise forms.ValidationError("Account number should contain only digits")
        return account_number

class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'business_type', 'registration_number', 'tax_id']

class VerificationDocumentForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'document_file']
        
    def clean_document_file(self):
        document = self.cleaned_data.get('document_file')
        if document:
            if document.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File too large ( > 5MB )")
            
            file_type = document.name.split('.')[-1].lower()
            if file_type not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise forms.ValidationError("Unsupported file type. Please upload PDF, JPG, or PNG files.")
        return document