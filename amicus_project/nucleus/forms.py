# Import necessary modules from Django
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Profile, AIProfile

# Define a custom user creation form that extends Django's UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    # Add additional fields for gender, age, and description
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=False)
    age = forms.IntegerField(min_value=18, max_value=120, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    # Define the Meta class to specify the model and fields
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'gender', 'age', 'description')

    # Override the save method to handle the additional profile fields
    def save(self, commit=True):
        # Call the parent class's save method
        user = super().save(commit=False)
        if commit:
            # Save the user instance
            user.save()
            # Update the user's profile with the additional fields
            user.profile.gender = self.cleaned_data.get('gender')
            user.profile.age = self.cleaned_data.get('age')
            user.profile.description = self.cleaned_data.get('description')
            user.profile.save()
        return user

# Define a form for updating user profiles
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_name', 'user_age', 'user_gender', 'user_description']

# Define a custom password change form
class CustomPasswordChangeForm(PasswordChangeForm):
    # Define the Meta class to specify the model
    class Meta:
        model = CustomUser

# Define a form for the AI profile
class AIProfileForm(forms.ModelForm):
    class Meta:
        model = AIProfile
        fields = ['ai_name', 'ai_age', 'ai_physical_appearance', 'ai_personality', 'ai_hobbies']
