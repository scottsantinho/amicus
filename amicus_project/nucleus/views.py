# Import necessary modules from Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, CustomPasswordChangeForm, AIProfileForm
from .models import AIProfile, Profile  # Change UserProfile to Profile

# Define the signup view function
def signup(request):
    """
    Handle user registration.
    """
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = CustomUserCreationForm(request.POST)
        # Validate the form
        if form.is_valid():
            # Save the new user
            user = form.save()
            # Log the user in
            login(request, user)
            # Redirect to the home page (or any other desired page)
            return redirect('home')
    else:
        # If it's a GET request, create an empty form
        form = CustomUserCreationForm()
    
    # Render the signup template with the form
    return render(request, 'nucleus/signup.html', {'form': form})

# Define the update_profile view function, requiring login
@login_required
def update_profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    ai_profile, created = AIProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=user_profile)
        ai_profile_form = AIProfileForm(request.POST, instance=ai_profile)
        if profile_form.is_valid() and ai_profile_form.is_valid():
            profile_form.save()
            ai_profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=user_profile)
        ai_profile_form = AIProfileForm(instance=ai_profile)
    
    return render(request, 'nucleus/profile.html', {
        'profile_form': profile_form,
        'ai_profile_form': ai_profile_form
    })

# Define the profile view function, requiring login
@login_required
def profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    ai_profile, created = AIProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user_profile)
        ai_profile_form = AIProfileForm(request.POST, instance=ai_profile)
        if profile_form.is_valid() and ai_profile_form.is_valid():
            profile_form.save()
            ai_profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=user_profile)
        ai_profile_form = AIProfileForm(instance=ai_profile)
    
    return render(request, 'nucleus/profile.html', {
        'form': profile_form,
        'ai_form': ai_profile_form
    })

# Define the home view function
def home(request):
    """
    Render the home page.
    """
    # Render the home template
    return render(request, 'nucleus/home.html')

# Define the profile_view function, requiring login
@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    ai_profile, created = AIProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        ai_profile_form = AIProfileForm(request.POST, instance=ai_profile)
        if profile_form.is_valid() and ai_profile_form.is_valid():
            profile_form.save()
            ai_profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
        ai_profile_form = AIProfileForm(instance=ai_profile)

    context = {
        'form': profile_form,
        'ai_form': ai_profile_form,
    }
    return render(request, 'nucleus/profile.html', context)
