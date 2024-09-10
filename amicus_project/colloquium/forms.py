from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': '3',
                'placeholder': 'Type your message here...',
            }),
        }
        labels = {
            'content': '',
        }
