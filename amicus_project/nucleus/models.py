# Import necessary modules from Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Define a custom user model that extends Django's AbstractUser
class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    # Add any additional fields for CustomUser if needed
    # For example:
    # is_premium = models.BooleanField(default=False)

    # Define string representation of the CustomUser model
    def __str__(self):
        return self.username

# Define a Profile model to store additional user information
class Profile(models.Model):
    """
    User profile model with additional information.
    """
    # Define gender choices as a list of tuples
    GENDER_CHOICES = [
        ('M', 'Man'),
        ('W', 'Woman'),
        ('O', 'Other'),
    ]

    # Create a one-to-one relationship with the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # Define a gender field with predefined choices
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # Define an age field with validators for minimum and maximum values
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        null=True,
        blank=True
    )

    # Define a description field for additional user information
    description = models.TextField(max_length=500, blank=True)

    # Define string representation of the Profile model
    def __str__(self):
        return f"{self.user.username}'s profile"

# Define a signal receiver function to create or update user profile
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create or update user profile.
    """
    # Create a Profile object when a new User is created
    if created:
        Profile.objects.create(user=instance)
    # Save the profile whenever the user is saved
    instance.profile.save()

# Define a new AIProfile model
class AIProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    physical_appearance = models.TextField(null=True, blank=True)
    personality = models.TextField(null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s AI Profile"

