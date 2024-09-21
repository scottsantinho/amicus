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
# Import HttpResponse for handling HTTP responses
from django.http import HttpResponse

# Define a view for listing conversations, requiring login
class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'colloquium/conversation_list.html'  # Change this line
    context_object_name = 'conversations'

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversations = context['conversations']
        active_conversation = None
        form = MessageForm()

        conversation_id = self.request.GET.get('conversation_id')
        if conversation_id:
            active_conversation = get_object_or_404(Conversation, id=conversation_id, user=self.request.user)
        elif conversations.exists():
            active_conversation = conversations.first()

        if active_conversation:
            # Refresh the conversation to get the latest messages
            active_conversation.refresh_from_db()

        context.update({
            'conversation': active_conversation,
            'form': form,
        })

        return context

# Define a view for displaying a single conversation, requiring login
class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'colloquium/conversation_detail.html'
    context_object_name = 'conversation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
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
            print(f"User message saved: {message.content}")  # Debug print

            context = get_conversation_context(conversation, request.user, max_tokens=8000)
            prompt = f"{context}\n\nUser: {message.content}\nAI:"

            try:
                os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
                replicate.api_key = settings.REPLICATE_API_TOKEN

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
                print(f"AI response generated: {ai_response}")  # Debug print

                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=ai_response.strip(),
                    is_user=False
                )
                print(f"AI message saved: {ai_message.content}")  # Debug print

                conversation.save()
            except replicate.exceptions.ReplicateError as e:
                print(f"Replicate API error: {str(e)}")
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=f"I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again later.",
                    is_user=False
                )
            except Exception as e:
                print(f"Error generating AI response: {str(e)}")
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=f"I'm sorry, but I encountered an unexpected error. Please try again later.",
                    is_user=False
                )

            if request.headers.get('HX-Request'):
                return render(request, 'colloquium/message_list.html', {'messages': [message, ai_message]})
            else:
                return redirect('conversation_list')

    return redirect('conversation_list')

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    # Create a new conversation and associate it with the current user
    conversation = Conversation.objects.create(user=request.user)
    # Redirect to the conversation detail page
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

# Define a view for deleting a single conversation, requiring login
@login_required
def delete_conversation(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    conversation.is_active = False
    conversation.save()
    messages.success(request, f"Conversation {pk} has been deleted.")
    return redirect('conversation_list')
