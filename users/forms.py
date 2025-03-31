# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomerSignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
        return user

class ServiceProviderSignupForm(UserCreationForm):
    company_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'company_name', 'address', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'service_provider'
        user.company_name = self.cleaned_data.get('company_name')
        user.address = self.cleaned_data.get('address')
        if commit:
            user.save()
        return user
    
class ProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['date_of_birth', 'id_number']