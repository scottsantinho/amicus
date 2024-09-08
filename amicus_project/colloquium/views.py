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
import os
import replicate
from django.conf import settings
from nucleus.models import CustomUser, Profile  # Assuming your CustomUser model is in the nucleus app
from django.views.decorators.http import require_POST
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
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.is_user = True
            message.save()

            # Get the conversation context with a rolling window of 8000 tokens
            context = get_conversation_context(conversation, request.user, max_tokens=8000)

            # Generate AI response
            prompt = f"{context}\n\nUser: {message.content}\nAI:"

            # Use the REPLICATE_API_TOKEN from settings
            replicate.api_key = settings.REPLICATE_API_TOKEN

            try:
                # Stream the response from Llama 3 70B
                ai_response = ""
                for event in replicate.stream(
                    "meta/meta-llama-3-70b-instruct",
                    input={
                        "prompt": prompt,
                        "max_new_tokens": 500,
                        "temperature": 0.7,
                    },
                ):
                    ai_response += str(event)

                # Create AI message
                Message.objects.create(
                    conversation=conversation,
                    content=ai_response.strip(),
                    is_user=False
                )

                conversation.save()
            except Exception as e:
                print(f"Error: {str(e)}")
                # Create an error message
                Message.objects.create(
                    conversation=conversation,
                    content=f"Sorry, I couldn't generate a response at this time. Error: {type(e).__name__}",
                    is_user=False
                )

            return redirect('conversation_detail', pk=pk)
    return redirect('conversation_detail', pk=pk)

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    # Create a new conversation for the current user
    conversation = Conversation.objects.create(user=request.user)
    # Redirect to the detail page of the newly created conversation
    return redirect('conversation_detail', pk=conversation.pk)

def get_conversation_context(conversation, user, max_tokens=8000):
    # Get user profile information
    profile = user.profile
    user_profile = f"User Profile: Age: {profile.age or 'Not specified'}, Gender: {profile.get_gender_display() or 'Not specified'}, Description: {profile.description or 'Not provided'}"
    
    # Get all messages from the conversation, ordered from newest to oldest
    messages = conversation.messages.order_by('-timestamp')
    
    context_messages = []
    estimated_token_count = len(user_profile.split())  # Rough estimate of tokens in user profile
    
    # Iterate through messages, adding them to the context until we reach the estimated token limit
    for msg in messages:
        message_text = f"{'User' if msg.is_user else 'AI'}: {msg.content}"
        estimated_message_tokens = len(message_text.split())
        
        if estimated_token_count + estimated_message_tokens > max_tokens:
            break
        
        context_messages.insert(0, message_text)  # Insert at the beginning to maintain chronological order
        estimated_token_count += estimated_message_tokens
    
    # Combine everything into a single context string
    context = f"{user_profile}\n\nConversation History:\n" + "\n".join(context_messages)
    
    return context

@login_required
@require_POST
def delete_conversations(request):
    conversation_ids = request.POST.getlist('conversation_ids')
    Conversation.objects.filter(id__in=conversation_ids, user=request.user).update(is_active=False)
    messages.success(request, f"{len(conversation_ids)} conversation(s) deleted successfully.")
    return redirect('conversation_list')
