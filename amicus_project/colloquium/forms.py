from django import forms
from .models import Message

# Define a form class for the Message model
class MessageForm(forms.ModelForm):
    # Define the Meta class to provide metadata about the form
    class Meta:
        # Specify the model that this form is associated with
        model = Message
        # Specify which fields from the model should be included in the form
        fields = ['content']
        # Define custom widgets for form fields
        widgets = {
            # Customize the 'content' field widget
            'content': forms.Textarea(attrs={
                # Set CSS classes for styling
                'class': 'w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                # Set the number of rows for the textarea
                'rows': '3',
                # Set a placeholder text for the textarea
                'placeholder': 'Type your message here...',
            }),
        }
        # Define custom labels for form fields
        labels = {
            # Remove the label for the 'content' field
            'content': '',
        }
