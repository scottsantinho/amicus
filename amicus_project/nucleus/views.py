from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm

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
    # Initialize password_form to None
    password_form = None

    if request.method == 'POST':
        # Check if the user is updating profile or changing password
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if profile_form.is_valid():
                profile = profile_form.save()
                messages.success(request, 'Your profile was successfully updated.')
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated.')
                return redirect('profile')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        password_form = CustomPasswordChangeForm(request.user)
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'nucleus/update_profile.html', context)

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
