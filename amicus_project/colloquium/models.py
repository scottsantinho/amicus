from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

# Define the Conversation model
class Conversation(models.Model):
    # Create a foreign key relationship with the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    # Define a character field for the conversation name
    name = models.CharField(max_length=255, blank=True, null=True)
    # Add a timestamp for when the conversation was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Add a boolean field to indicate if the conversation is active
    is_active = models.BooleanField(default=True)

    # Define a string representation of the Conversation model
    def __str__(self):
        return f"Conversation {self.id}" if not self.name else self.name

# Define the Message model
class Message(models.Model):
    # Create a foreign key relationship with the Conversation model
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    # Define a text field for the message content
    content = models.TextField()
    # Add a timestamp for when the message was created
    timestamp = models.DateTimeField(auto_now_add=True)
    # Add a boolean field to indicate if the message is from the user
    is_user = models.BooleanField(default=True)

    # Define a string representation of the Message model
    def __str__(self):
        return f"Message in Conversation {self.conversation.id} - {'User' if self.is_user else 'AI'}"

    # Define metadata for the Message model
    class Meta:
        # Set the default ordering for messages
        ordering = ['timestamp']
