# Import necessary modules from Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, AIProfile

# Define an inline admin class for the Profile model
class ProfileInline(admin.StackedInline):
    # Specify the model to be used for the inline
    model = Profile
    # Prevent deletion of the profile from the admin interface
    can_delete = False
    # Set the plural name for the inline in the admin interface
    verbose_name_plural = 'Profile'

# Define an inline admin class for the AIProfile model
class AIProfileInline(admin.StackedInline):
    # Specify the model to be used for the inline
    model = AIProfile
    # Prevent deletion of the AIProfile from the admin interface
    can_delete = False
    # Set the plural name for the inline in the admin interface
    verbose_name_plural = 'AI Profile'

# Define a custom admin class for the CustomUser model
class CustomUserAdmin(UserAdmin):
    # Include the ProfileInline and AIProfileInline in the CustomUser admin interface
    inlines = (ProfileInline, AIProfileInline)
    # Define the display fields for the CustomUser model
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    # Define the filter fields for the CustomUser model
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Define the search fields for the CustomUser model
    search_fields = ('username', 'first_name', 'last_name', 'email')
    # Define the ordering for the CustomUser model
    ordering = ('username',)

# Register the CustomUser model with the CustomUserAdmin class
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(AIProfile)
