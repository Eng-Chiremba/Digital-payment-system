from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from .forms import CustomerSignupForm, ServiceProviderSignupForm, ProfileCompletionForm

User = get_user_model()



def customer_signup(request):
    """
    Signup view for customers.
    """
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose another.")
            else:
                user = form.save()
                auth_login(request, user)
                return redirect('complete-profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomerSignupForm()
    return render(request, 'users/customer_signup.html', {'form': form})

def business_signup(request):
    """
    Signup view for service providers.
    """
    if request.method == 'POST':
        form = ServiceProviderSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('complete-profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ServiceProviderSignupForm()
    return render(request, 'users/service_provider_signup.html', {'form': form})

class CustomLoginView(LoginView):
    """
    Custom login view that redirects users based on their user type.
    """
    template_name = 'users/login.html'
    authentication_form = AuthenticationForm
    
    def get_success_url(self):
        user = self.request.user
        
        # Check if profile completion is needed
        if not user.is_profile_completed:
            return reverse('complete-profile')
            
        # Redirect based on user type
        if user.user_type == 'customer':
            return reverse('customer-dashboard')
        elif user.user_type == 'service_provider':
            return reverse('provider-dashboard')
        return reverse('landing')  # Fallback to landing page

@login_required
def complete_profile(request):
    """
    Profile completion view for collecting additional required info.
    """
    user = request.user
    if user.is_profile_completed:
        # Redirect to appropriate dashboard if profile already completed
        if user.user_type == 'customer':
            return redirect('customer-dashboard')
        else:
            return redirect('provider-dashboard')

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=True)
            user.is_profile_completed = True
            user.save()
            
            messages.success(request, "Profile completed successfully!")
            
            # Redirect to appropriate dashboard
            if user.user_type == 'customer':
                return redirect('customer-dashboard')
            else:
                return redirect('provider-dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProfileCompletionForm(instance=user)
    
    context = {
        'form': form,
        'user_type': user.user_type.replace('_', ' ').title()  # For display purposes
    }
    
    return render(request, 'users/complete_profile.html', context)

'''
kana washinga kutemwa nemusoro shandisa view iri

def business_signup(request):
    """
    Signup view for service providers.
    """
    form = ServiceProviderSignupForm()
    if request.method == 'POST':
        form = ServiceProviderSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return redirect('provider-dashboard')  # service provider home page that will be dfferent from the customer
        else:
            form = ServiceProviderSignupForm()
    return render(request, 'users/service_provider_signup.html', {'form': form})

@login_required
def complete_profile(request):
    user = request.user

    if user.date_of_birth and user.id_number:
        return redirect('home')  # Skip if already completed

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()

            #  authentication backend
            if not hasattr(user, 'backend'):
                backends = get_backends()[0]
                for backend in backends:
                    if user.has_usable_password():
                        user.backend = backend.__module__ + '.' + backend.__class__.__name__
                        break
            
            login(request, user)  # Log the user in after updating their profile
            return redirect('customer-dashboard')  # Redirect to home page after login

    else:
        form = ProfileCompletionForm(instance=user)

    return render(request, 'users/complete_profile.html', {'form': form})'''