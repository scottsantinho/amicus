# Import necessary modules from Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm, AIProfileForm
from .models import AIProfile

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
            # Get the age from the cleaned form data
            age = form.cleaned_data.get('age')
            # Check if the user is under 18
            if age and age < 18:
                # Display an error message for underage users
                messages.error(request, "Sorry, come back when you'll be 18!")
                # Render the signup page with the form
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

# Define the update_profile view function, requiring login
@login_required
def update_profile(request):
    """
    Handle profile updates for logged-in users.
    """
    # Initialize password_form to None
    password_form = None

    # Check if the request method is POST
    if request.method == 'POST':
        # Check if the user is updating profile or changing password
        if 'update_profile' in request.POST:
            # Create a form instance with the submitted profile data
            profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            ai_profile_form = AIProfileForm(request.POST, instance=getattr(request.user, 'aiprofile', None))
            # Validate the form
            if profile_form.is_valid() and ai_profile_form.is_valid():
                # Save the updated profile
                profile = profile_form.save()
                ai_profile = ai_profile_form.save(commit=False)
                ai_profile.user = request.user
                ai_profile.save()
                # Display a success message
                messages.success(request, 'Your profile was successfully updated.')
                # Redirect to the profile page
                return redirect('profile')
        elif 'change_password' in request.POST:
            # Create a form instance with the submitted password data
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            # Validate the form
            if password_form.is_valid():
                # Save the new password
                user = password_form.save()
                # Update the session with the new password hash
                update_session_auth_hash(request, user)
                # Display a success message
                messages.success(request, 'Your password was successfully updated.')
                # Redirect to the profile page
                return redirect('profile')
        else:
            # Display an error message for invalid form submission
            messages.error(request, 'Invalid form submission.')
    else:
        # If it's a GET request, create empty forms
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        ai_profile_form = AIProfileForm(instance=getattr(request.user, 'aiprofile', None))
        password_form = CustomPasswordChangeForm(request.user)
    
    # Prepare the context for the template
    context = {
        'profile_form': profile_form,
        'ai_profile_form': ai_profile_form,
        'password_form': password_form
    }
    # Render the update profile template with the context
    return render(request, 'nucleus/update_profile.html', context)

# Define the profile view function, requiring login
@login_required
def profile(request):
    ai_profile, created = AIProfile.objects.get_or_create(user=request.user)
    return render(request, 'nucleus/profile.html', {'ai_profile': ai_profile})

# Define the home view function
def home(request):
    """
    Render the home page.
    """
    # Render the home template
    return render(request, 'nucleus/home.html')
