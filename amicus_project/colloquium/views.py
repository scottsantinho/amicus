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
# Import HTTP POST decorator and require_http_methods
from django.views.decorators.http import require_POST, require_http_methods
# Import messages framework
from django.contrib import messages
# Import HttpResponse for handling HTTP responses
from django.http import HttpResponse
# Import JsonResponse for JSON response
from django.http import JsonResponse
# Import json for handling JSON data
import json

# Define a view for listing conversations, requiring login
class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'colloquium/conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user, is_active=True).order_by('-created_at')

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
        context['ai_profile'] = self.object.user.aiprofile
        context['messages'] = self.object.messages.all().order_by('timestamp')
        context['user_name'] = self.request.user.profile.user_name or self.request.user.username
        context['ai_name'] = self.object.user.aiprofile.ai_name or "AI Assistant"
        return context

# Define a view for creating a new message, requiring login
@login_required
@require_http_methods(["POST"])
def new_message(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    
    # Try to parse JSON data
    try:
        data = json.loads(request.body)
        message_content = data.get('content')
    except json.JSONDecodeError:
        # If JSON parsing fails, try to get data from POST
        message_content = request.POST.get('content')

    if message_content:
        message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            is_user=True
        )
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
            return JsonResponse({'success': True, 'ai_response': ai_message.content})
        except replicate.exceptions.ReplicateError as e:
            print(f"Replicate API error: {str(e)}")
            ai_response = "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again later."
        except Exception as e:
            print(f"Error generating AI response: {str(e)}")
            ai_response = "I'm sorry, but I encountered an unexpected error. Please try again later."

        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        return JsonResponse({'success': True, 'ai_response': ai_response})

    return JsonResponse({'success': False, 'error': 'No message content provided'}, status=400)

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    if request.method == 'POST':
        conversation = Conversation.objects.create(user=request.user)
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.pk,
            'html': render(request, 'colloquium/conversation_detail.html', {'conversation': conversation, 'form': MessageForm()}).content.decode('utf-8')
        })
    return JsonResponse({'success': False}, status=400)

# Function to get conversation context
def get_conversation_context(conversation, user, max_tokens=8000):
    profile = user.profile
    user_profile = f"User Profile: Name: {profile.user_name or 'Not specified'}, Age: {profile.user_age or 'Not specified'}, Gender: {profile.get_user_gender_display() or 'Not specified'}, Description: {profile.user_description or 'Not provided'}"
    
    ai_profile, created = AIProfile.objects.get_or_create(user=user)
    ai_profile_context = f"""
    AI Assistant Profile:
    Name: {ai_profile.ai_name or 'Not specified'}
    Age: {ai_profile.ai_age or 'Not specified'}
    Physical Appearance: {ai_profile.ai_physical_appearance or 'Not specified'}
    Personality: {ai_profile.ai_personality or 'Not specified'}
    Hobbies: {ai_profile.ai_hobbies or 'Not specified'}
    
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
    return JsonResponse({'success': True, 'message': f"Conversation {pk} has been deleted."})

# Define a view for sending a message, requiring login and POST method
@login_required
@require_POST
def send_message(request, conversation_id):
    print(f"Received request to send_message for conversation {conversation_id}")  # Debug print
    conversation = get_object_or_404(Conversation, pk=conversation_id, user=request.user)
    try:
        data = json.loads(request.body)
        content = data.get('content')
        print(f"Received content: {content}")  # Debug print
    except json.JSONDecodeError:
        print("Failed to parse JSON data")  # Debug print
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)

    if content:
        user_profile = request.user.profile
        user_name = user_profile.user_name or request.user.username
        message = Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=True
        )
        print(f"User message created: {message.id}")  # Debug print

        # Use the existing new_message logic to get AI response
        ai_response = get_ai_response(conversation, content)
        print(f"AI response generated: {ai_response[:50]}...")  # Debug print

        ai_profile = conversation.user.aiprofile
        ai_name = ai_profile.ai_name or "AI Assistant"
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        print(f"AI message created: {ai_message.id}")  # Debug print

        return JsonResponse({
            'success': True, 
            'user_message': {'name': user_name, 'content': content, 'timestamp': message.timestamp.strftime("%B %d, %Y %H:%M")},
            'ai_message': {'name': ai_name, 'content': ai_response, 'timestamp': ai_message.timestamp.strftime("%B %d, %Y %H:%M")}
        })
    
    print("No message content provided")  # Debug print
    return JsonResponse({'success': False, 'error': 'No message content provided'}, status=400)

# Add this helper function to get AI response
def get_ai_response(conversation, user_message):
    context = get_conversation_context(conversation, conversation.user)
    prompt = f"{context}\n\nUser: {user_message}\nAI:"

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
        
        return ai_response.strip()
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return "I'm sorry, but I encountered an unexpected error. Please try again later."

from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import Conversation
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

@method_decorator(require_POST, name='dispatch')
class ConversationEditView(LoginRequiredMixin, UpdateView):
    model = Conversation
    fields = ['name']
    template_name = 'colloquium/conversation_edit.html'
    
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})
