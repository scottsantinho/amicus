from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm

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
            age = form.cleaned_data.get('age')
            if age and age < 18:
                messages.error(request, "Sorry, come back when you'll be 18!")
                return render(request, 'nucleus/signup.html', {'form': form})
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

@login_required
def update_profile(request):
    """
    Handle profile updates for logged-in users.
    """
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        # Create a form instance with the submitted data and the user's current profile
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        # Validate the form
        if form.is_valid():
            # Save the updated profile
            form.save()
            # Redirect to the profile page (or any other desired page)
            return redirect('profile')
    else:
        # If it's a GET request, create a form pre-filled with the user's current profile data
        form = ProfileUpdateForm(instance=request.user.profile)
    
    # Render the update_profile template with the form
    return render(request, 'nucleus/update_profile.html', {'form': form})

@login_required
def profile(request):
    """
    Display the user's profile.
    """
    # Render the profile template with the user's profile data
    return render(request, 'nucleus/profile.html', {'profile': request.user.profile})

def home(request):
    """
    Render the home page.
    """
    return render(request, 'nucleus/home.html')
