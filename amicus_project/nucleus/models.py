from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    # Add any additional fields for CustomUser if needed
    # For example:
    # is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Profile(models.Model):
    """
    User profile model with additional information.
    """
    # Define gender choices
    GENDER_CHOICES = [
        ('M', 'Man'),
        ('W', 'Woman'),
        ('O', 'Other'),
    ]

    # Link to the CustomUser model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # Gender field with predefined choices
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # Age field with validators
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(120)],
        null=True,
        blank=True
    )

    # Description field
    description = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

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
