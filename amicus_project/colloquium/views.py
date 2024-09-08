# Import necessary modules from Django
from django.shortcuts import render, get_object_or_404, redirect
# Import generic class-based views
from django.views.generic import ListView, DetailView
# Import mixin for requiring login
from django.contrib.auth.mixins import LoginRequiredMixin
# Import decorator for requiring login
from django.contrib.auth.decorators import login_required
# Import reverse function for URL reversing
from django.urls import reverse
# Import models from current directory
from .models import Conversation, Message
# Import forms from current directory
from .forms import MessageForm
# Import os module for environment variables
import os
# Import replicate for AI model integration
import replicate
# Import settings from Django configuration
from django.conf import settings
# Import user-related models from nucleus app
from nucleus.models import CustomUser, Profile, AIProfile
# Import HTTP POST decorator
from django.views.decorators.http import require_POST
# Import messages framework
from django.contrib import messages

# Define a view for listing conversations, requiring login
class ConversationListView(LoginRequiredMixin, ListView):
    # Specify the model to use
    model = Conversation
    # Specify the template to render
    template_name = 'colloquium/conversation_list.html'
    # Specify the name of the context variable in the template
    context_object_name = 'conversations'

    # Override the get_queryset method to filter conversations
    def get_queryset(self):
        # Return conversations for the current user, ordered by most recent update
        return Conversation.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')

# Define a view for displaying a single conversation, requiring login
class ConversationDetailView(LoginRequiredMixin, DetailView):
    # Specify the model to use
    model = Conversation
    # Specify the template to render
    template_name = 'colloquium/conversation_detail.html'
    # Specify the name of the context variable in the template
    context_object_name = 'conversation'

    # Override the get_context_data method to add form to context
    def get_context_data(self, **kwargs):
        # Call the parent class's get_context_data method
        context = super().get_context_data(**kwargs)
        # Add a new MessageForm instance to the context
        context['form'] = MessageForm()
        # Return the updated context
        return context

# Define a view for creating a new message, requiring login
@login_required
def new_message(request, pk):
    # Get the conversation object or return 404 if not found
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    # Check if the request method is POST
    if request.method == 'POST':
        # Create a form instance with POST data
        form = MessageForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Create a new message object without saving to the database
            message = form.save(commit=False)
            # Set the conversation for the message
            message.conversation = conversation
            # Set the message as user-generated
            message.is_user = True
            # Save the message to the database
            message.save()

            # Get the conversation context with a rolling window of 8000 tokens
            context = get_conversation_context(conversation, request.user, max_tokens=8000)

            # Generate AI response prompt
            prompt = f"{context}\n\nUser: {message.content}\nAI:"

            # Set the API key for Replicate
            os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            replicate.api_key = settings.REPLICATE_API_TOKEN

            try:
                # Stream the response from Llama 3 70B
                ai_response = ""
                # Iterate through the streamed response
                for event in replicate.stream(
                    "meta/meta-llama-3-70b-instruct",
                    input={
                        "prompt": prompt,
                        "max_new_tokens": 500,
                        "temperature": 0.7,
                    },
                ):
                    # Accumulate the response
                    ai_response += str(event)

                # Create AI message in the database
                Message.objects.create(
                    conversation=conversation,
                    content=ai_response.strip(),
                    is_user=False
                )

                # Save the updated conversation
                conversation.save()
            except Exception as e:
                # Print the error message
                print(f"Error: {str(e)}")
                # Create an error message in the database
                Message.objects.create(
                    conversation=conversation,
                    content=f"Sorry, I couldn't generate a response at this time. Error: {type(e).__name__}",
                    is_user=False
                )

            # Redirect to the conversation detail page
            return redirect('conversation_detail', pk=pk)
    # If not POST request, redirect to the conversation detail page
    return redirect('conversation_detail', pk=pk)

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    # Create a new conversation for the current user
    conversation = Conversation.objects.create(user=request.user)
    # Redirect to the detail page of the newly created conversation
    return redirect('conversation_detail', pk=conversation.pk)

# Function to get conversation context
def get_conversation_context(conversation, user, max_tokens=8000):
    # Get user profile information
    profile = user.profile
    # Create user profile string
    user_profile = f"User Profile: Age: {profile.age or 'Not specified'}, Gender: {profile.get_gender_display() or 'Not specified'}, Description: {profile.description or 'Not provided'}"
    
    # Get or create AI profile information
    ai_profile, created = AIProfile.objects.get_or_create(user=user)
    # Create AI profile context string
    ai_profile_context = f"""
    AI Assistant Profile:
    Name: {ai_profile.name or 'Not specified'}
    Age: {ai_profile.age or 'Not specified'}
    Physical Appearance: {ai_profile.physical_appearance or 'Not specified'}
    Personality: {ai_profile.personality or 'Not specified'}
    Hobbies: {ai_profile.hobbies or 'Not specified'}
    
    You are an AI assistant with the above profile. Please respond to the user's messages in a way that reflects your personality, age, and interests. Your responses should be consistent with your profile.
    """
    
    # Get all messages from the conversation, ordered from newest to oldest
    messages = conversation.messages.order_by('-timestamp')
    
    # Initialize empty list for context messages
    context_messages = []
    # Calculate initial estimated token count
    estimated_token_count = len(user_profile.split()) + len(ai_profile_context.split())
    
    # Iterate through messages, adding them to the context until we reach the estimated token limit
    for msg in messages:
        # Create message text string
        message_text = f"{'User' if msg.is_user else 'AI'}: {msg.content}"
        # Estimate token count for the message
        estimated_message_tokens = len(message_text.split())
        
        # Check if adding this message would exceed the token limit
        if estimated_token_count + estimated_message_tokens > max_tokens:
            break
        
        # Insert message at the beginning to maintain chronological order
        context_messages.insert(0, message_text)
        # Update estimated token count
        estimated_token_count += estimated_message_tokens
    
    # Combine everything into a single context string
    context = f"{user_profile}\n\n{ai_profile_context}\n\nConversation History:\n" + "\n".join(context_messages)
    
    # Return the complete context
    return context

# Define a view for deleting conversations, requiring login and POST method
@login_required
@require_POST
def delete_conversations(request):
    # Get list of conversation IDs from POST data
    conversation_ids = request.POST.getlist('conversation_ids')
    # Update conversations to set is_active to False (soft delete)
    Conversation.objects.filter(id__in=conversation_ids, user=request.user).update(is_active=False)
    # Add success message
    messages.success(request, f"{len(conversation_ids)} conversation(s) deleted successfully.")
    # Redirect to conversation list page
    return redirect('conversation_list')
