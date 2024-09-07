from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile

class CustomUserCreationForm(UserCreationForm):
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=False)
    age = forms.IntegerField(min_value=18, max_value=120, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'gender', 'age', 'description')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.profile.gender = self.cleaned_data.get('gender')
            user.profile.age = self.cleaned_data.get('age')
            user.profile.description = self.cleaned_data.get('description')
            user.profile.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['gender', 'age', 'description']
