from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser

class CustomerSignupForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20, 
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        user.username = self.cleaned_data.get('phone_number')  # Use phone number as username
        user.phone_number = self.cleaned_data.get('phone_number')
        if commit:
            user.save()
        return user

class ServiceProviderSignupForm(UserCreationForm):
    company_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    phone_number = forms.CharField(
        max_length=20, 
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'company_name', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'service_provider'
        user.username = self.cleaned_data.get('phone_number')  # Use phone number as username
        user.phone_number = self.cleaned_data.get('phone_number')
        user.company_name = self.cleaned_data.get('company_name')
        user.address = self.cleaned_data.get('address')
        if commit:
            user.save()
        return user
    
class ProfileCompletionForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    id_number = forms.CharField(
        max_length=50, 
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9-]+$',
                message="ID number must contain only letters, numbers, and hyphens."
            )
        ]
    )
    
    class Meta:
        model = CustomUser
        fields = ['date_of_birth', 'id_number']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_profile_completed = True
        if commit:
            user.save()
        return user