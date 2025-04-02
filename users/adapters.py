from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from .models import CustomUser

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        
        # Check if profile completion is needed
        if not user.is_profile_completed:
            return reverse('complete-profile')
            
        # Redirect based on user type
        if user.user_type == 'customer':
            return reverse('customer-dashboard')
        elif user.user_type == 'service_provider':
            return reverse('provider-dashboard')
        return reverse('home')
    
    def save_user(self, request, user, form, commit=True):
        # Set default user type from session if available
        user_type = request.session.get('user_type', 'customer')
        user.user_type = user_type
        
        # Get phone number if available
        data = form.cleaned_data
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
            
        # Save the user
        user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Store user type from session if set
        if 'user_type' in request.session:
            sociallogin.user.user_type = request.session['user_type']
    
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # Get email from social account
        if 'email' in data:
            user.email = data['email']
            
        # Set default user type from session if available
        user_type = request.session.get('user_type', 'customer')
        user.user_type = user_type
        
        return user
        
    def get_connect_redirect_url(self, request, socialaccount):
        # After connecting social account, redirect to profile completion if needed
        if not request.user.is_profile_completed:
            return reverse('complete-profile')
            
        # Otherwise redirect based on user type
        if request.user.user_type == 'customer':
            return reverse('customer-dashboard')
        elif request.user.user_type == 'service_provider':
            return reverse('provider-dashboard')
        return reverse('home')

