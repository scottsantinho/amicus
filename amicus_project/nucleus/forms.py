# Import necessary modules from Django
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Profile

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
class ProfileUpdateForm(forms.ModelForm):
    # Add an email field to the form
    email = forms.EmailField()

    # Define the Meta class to specify the model and fields
    class Meta:
        model = Profile
        fields = ['gender', 'age', 'description', 'email']

    # Override the constructor to set the initial value of the email field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email

    # Override the save method to update both the profile and user email
    def save(self, commit=True):
        # Call the parent class's save method
        profile = super().save(commit=False)
        if commit:
            # Save the profile instance
            profile.save()
            # Update the user's email
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
        return profile

    def clean_age(self):
        # Get the age value from the cleaned data
        age = self.cleaned_data.get('age')
        
        # Check if age is provided (it's optional)
        if age is not None:
            # Validate age against the model's validators
            if age < 18 or age > 120:
                raise ValidationError("Age must be between 18 and 120.")
        
        return age

# Define a custom password change form
class CustomPasswordChangeForm(PasswordChangeForm):
    # Define the Meta class to specify the model
    class Meta:
        model = CustomUser
