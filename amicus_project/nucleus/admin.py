# Import necessary modules from Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

# Define an inline admin class for the Profile model
class ProfileInline(admin.StackedInline):
    # Specify the model to be used for the inline
    model = Profile
    # Prevent deletion of the profile from the admin interface
    can_delete = False
    # Set the plural name for the inline in the admin interface
    verbose_name_plural = 'Profile'

# Define a custom admin class for the CustomUser model
class CustomUserAdmin(UserAdmin):
    # Include the ProfileInline in the CustomUser admin interface
    inlines = (ProfileInline,)

# Register the CustomUser model with the CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)
