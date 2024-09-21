from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user = models.BooleanField(default=True)

    def __str__(self):
        return f"Message in Conversation {self.conversation.id} - {'User' if self.is_user else 'AI'}"

    class Meta:
        ordering = ['timestamp']
