# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import login, get_backends, load_backend
from django.contrib.auth.views import LoginView
from .forms import CustomerSignupForm, ServiceProviderSignupForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileCompletionForm
from django.urls import reverse

def landing(request):
    """
    Landing page where users select their role.
    """
    return render(request, 'users/landing.html')

def customer_signup(request):
    """
    Signup view for customers.
    """
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('complete-profile') 
    else:
        form = CustomerSignupForm()
    return render(request, 'users/customer_signup.html', {'form': form})

def business_signup(request):
    """ Signup view for service providers. """
    if request.method == 'POST':
        form = ServiceProviderSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return redirect('provider-dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = ServiceProviderSignupForm()
    return render(request, 'users/service_provider_signup.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view that redirects users based on their user type.
    """
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'customer':
            return reverse('customer-dashboard')
        elif user.user_type == 'service_provider':
            return reverse('provider-dashboard')
        return reverse('home')


@login_required
def complete_profile(request):
    user = request.user
    if user.date_of_birth and user.id_number:
        return redirect('home')  # Skip if already completed

    if request.method == 'POST':
        form = ProfileCompletionForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home') # take note 'home ' is only for debugging .. in production tichashandisa customer-dashboard
    else:
        form = ProfileCompletionForm(instance=user)
    return render(request, 'users/complete_profile.html', {'form': form})


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