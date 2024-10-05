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
    # Set the model for this view to Conversation
    model = Conversation
    # Specify the template to be used for rendering
    template_name = 'colloquium/conversation_list.html'
    # Set the name of the variable to be used in the template
    context_object_name = 'conversations'

    def get_queryset(self):
        # Return a queryset of active conversations for the current user, ordered by creation date
        return super().get_queryset().filter(user=self.request.user, is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        # Get the default context data
        context = super().get_context_data(**kwargs)
        # Get the conversations from the context
        conversations = context['conversations']
        # Initialize active_conversation as None
        active_conversation = None
        # Create a new MessageForm instance
        form = MessageForm()

        # Get the conversation_id from the GET parameters
        conversation_id = self.request.GET.get('conversation_id')
        if conversation_id:
            # If a conversation_id is provided, get that specific conversation
            active_conversation = get_object_or_404(Conversation, id=conversation_id, user=self.request.user)
        elif conversations.exists():
            # If no conversation_id is provided but conversations exist, use the first one
            active_conversation = conversations.first()

        if active_conversation:
            # Refresh the active conversation to get the latest data
            active_conversation.refresh_from_db()

        # Update the context with the active conversation and form
        context.update({
            'conversation': active_conversation,
            'form': form,
        })

        # Set a display name for each conversation
        for conversation in conversations:
            conversation.display_name = conversation.name or f"Conversation {conversation.id}"

        # Return the updated context
        return context

# Define a view for displaying a single conversation, requiring login
class ConversationDetailView(LoginRequiredMixin, DetailView):
    # Set the model for this view to Conversation
    model = Conversation
    # Specify the template to be used for rendering
    template_name = 'colloquium/conversation_detail.html'
    # Set the name of the variable to be used in the template
    context_object_name = 'conversation'

    def get_context_data(self, **kwargs):
        # Get the default context data
        context = super().get_context_data(**kwargs)
        # Add the AI profile to the context
        context['ai_profile'] = self.object.user.aiprofile
        # Add all messages of the conversation to the context, ordered by timestamp
        context['messages'] = self.object.messages.all().order_by('timestamp')
        # Add the user's name to the context
        context['user_name'] = self.request.user.profile.user_name or self.request.user.username
        # Add the AI's name to the context
        context['ai_name'] = self.object.user.aiprofile.ai_name or "AI Assistant"
        # Return the updated context
        return context

# Define a view for creating a new message, requiring login
@login_required
@require_http_methods(["POST"])
def new_message(request, pk):
    # Get the conversation object or return a 404 if not found
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    
    # Try to parse JSON data from the request body
    try:
        data = json.loads(request.body)
        message_content = data.get('content')
    except json.JSONDecodeError:
        # If JSON parsing fails, try to get data from POST
        message_content = request.POST.get('content')

    if message_content:
        # Create a new message object
        message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            is_user=True
        )
        # Print debug information
        print(f"User message saved: {message.content}")

        # Get the conversation context
        context = get_conversation_context(conversation, request.user, max_tokens=8000)
        # Create the prompt for the AI
        prompt = f"{context}\n\nUser: {message.content}\nAI:"

        try:
            # Set the Replicate API token
            os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
            replicate.api_key = settings.REPLICATE_API_TOKEN

            # Initialize the AI response
            ai_response = ""
            # Stream the AI response
            for event in replicate.stream(
                "meta/meta-llama-3-70b-instruct",
                input={
                    "prompt": prompt,
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                },
            ):
                ai_response += str(event)
            # Print debug information
            print(f"AI response generated: {ai_response}")

            # Create a new message object for the AI response
            ai_message = Message.objects.create(
                conversation=conversation,
                content=ai_response.strip(),
                is_user=False
            )
            # Print debug information
            print(f"AI message saved: {ai_message.content}")

            # Save the conversation
            conversation.save()
            # Return a JSON response with the AI's response
            return JsonResponse({'success': True, 'ai_response': ai_message.content})
        except replicate.exceptions.ReplicateError as e:
            # Handle Replicate API errors
            print(f"Replicate API error: {str(e)}")
            ai_response = "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again later."
        except Exception as e:
            # Handle other exceptions
            print(f"Error generating AI response: {str(e)}")
            ai_response = "I'm sorry, but I encountered an unexpected error. Please try again later."

        # Create a new message object for the AI response (in case of errors)
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        # Return a JSON response with the AI's response
        return JsonResponse({'success': True, 'ai_response': ai_response})

    # Return an error response if no message content was provided
    return JsonResponse({'success': False, 'error': 'No message content provided'}, status=400)

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    if request.method == 'POST':
        # Create a new conversation object
        conversation = Conversation.objects.create(user=request.user)
        # Return a JSON response with the new conversation details
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.pk,
            'html': render(request, 'colloquium/conversation_detail.html', {'conversation': conversation, 'form': MessageForm()}).content.decode('utf-8')
        })
    # Return an error response if the request method is not POST
    return JsonResponse({'success': False}, status=400)

# Function to get conversation context
def get_conversation_context(conversation, user, max_tokens=8000):
    # Get the user's profile
    profile = user.profile
    # Create a string with the user's profile information
    user_profile = f"User Profile: Name: {profile.user_name or 'Not specified'}, Age: {profile.user_age or 'Not specified'}, Gender: {profile.get_user_gender_display() or 'Not specified'}, Description: {profile.user_description or 'Not provided'}"
    
    # Get or create the AI profile
    ai_profile, created = AIProfile.objects.get_or_create(user=user)
    # Create a string with the AI's profile information
    ai_profile_context = f"""
    AI Assistant Profile:
    Name: {ai_profile.ai_name or 'Not specified'}
    Age: {ai_profile.ai_age or 'Not specified'}
    Physical Appearance: {ai_profile.ai_physical_appearance or 'Not specified'}
    Personality: {ai_profile.ai_personality or 'Not specified'}
    Hobbies: {ai_profile.ai_hobbies or 'Not specified'}
    
    You are an AI assistant with the above profile. Please respond to the user's messages in a way that reflects your personality, age, and interests. Your responses should be consistent with your profile.
    """
    
    # Create a string with instructions for code formatting
    code_formatting_instruction = """
    When providing code snippets in your responses, always format them using triple backticks and specify the language. For example:

    ```python
    def example_function():
        print("This is a formatted code snippet")
    ```

    This applies to all programming languages, including HTML, CSS, JavaScript, etc. Always specify the appropriate language after the opening backticks.
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
    
    # Join the context messages into a single string
    conversation_history = "\n".join(context_messages)
    
    # Combine everything into a single context string
    context = f"""
    {user_profile}
    {ai_profile_context}
    {code_formatting_instruction}
    
    Previous conversation:
    {conversation_history}
    """
    
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
    # Get the conversation object or return a 404 if not found
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    # Set is_active to False (soft delete)
    conversation.is_active = False
    # Save the conversation
    conversation.save()
    # Return a JSON response indicating success
    return JsonResponse({'success': True, 'message': f"Conversation {pk} has been deleted."})

# Define a view for sending a message, requiring login and POST method
@login_required
@require_POST
def send_message(request, conversation_id):
    # Print debug information
    print(f"Received request to send_message for conversation {conversation_id}")
    # Get the conversation object or return a 404 if not found
    conversation = get_object_or_404(Conversation, pk=conversation_id, user=request.user)
    try:
        # Try to parse JSON data from the request body
        data = json.loads(request.body)
        content = data.get('content')
        # Print debug information
        print(f"Received content: {content}")
    except json.JSONDecodeError:
        # Print debug information if JSON parsing fails
        print("Failed to parse JSON data")
        # Return an error response
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)

    if content:
        # Get the user's profile
        user_profile = request.user.profile
        # Get the user's name
        user_name = user_profile.user_name or request.user.username
        # Create a new message object
        message = Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=True
        )
        # Print debug information
        print(f"User message created: {message.id}")

        # Get AI response using the existing new_message logic
        ai_response = get_ai_response(conversation, content)
        # Print debug information
        print(f"AI response generated: {ai_response[:50]}...")

        # Get the AI profile
        ai_profile = conversation.user.aiprofile
        # Get the AI's name
        ai_name = ai_profile.ai_name or "AI Assistant"
        # Create a new message object for the AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        # Print debug information
        print(f"AI message created: {ai_message.id}")

        # Return a JSON response with both user and AI messages
        return JsonResponse({
            'success': True, 
            'user_message': {'name': user_name, 'content': content, 'timestamp': message.timestamp.strftime("%B %d, %Y %H:%M")},
            'ai_message': {'name': ai_name, 'content': ai_response, 'timestamp': ai_message.timestamp.strftime("%B %d, %Y %H:%M")}
        })
    
    # Print debug information if no message content was provided
    print("No message content provided")
    # Return an error response
    return JsonResponse({'success': False, 'error': 'No message content provided'}, status=400)

# Add this helper function to get AI response
import re

def format_code_blocks(text):
    # Regular expression to find code blocks
    code_block_regex = r'```(\w+)?\n(.*?)\n```'
    
    def replace_code_block(match):
        # Get the language and code from the regex match
        language = match.group(1) or ''
        code = match.group(2)
        # Return the formatted code block
        return f'```{language}\n{code}\n```'
    
    # Replace code blocks in the text
    formatted_text = re.sub(code_block_regex, replace_code_block, text, flags=re.DOTALL)
    # Return the formatted text
    return formatted_text

def get_ai_response(conversation, user_message):
    # Get the conversation context
    context = get_conversation_context(conversation, conversation.user)
    # Create the prompt for the AI
    prompt = f"{context}\n\nUser: {user_message}\nAI:"

    try:
        # Set the Replicate API token
        os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_TOKEN
        replicate.api_key = settings.REPLICATE_API_TOKEN

        # Initialize the AI response
        ai_response = ""
        # Stream the AI response
        for event in replicate.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7,
            },
        ):
            ai_response += str(event)
        
        # Apply code formatting to the AI response
        formatted_response = format_code_blocks(ai_response.strip())
        # Return the formatted response
        return formatted_response
    except Exception as e:
        # Print debug information if an error occurs
        print(f"Error generating AI response: {str(e)}")
        # Return an error message
        return "I'm sorry, but I encountered an unexpected error. Please try again later."

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class ConversationEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Get the conversation object or return a 404 if not found
        conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        # Get the new name from the data
        new_name = data.get('name')
        if new_name:
            # Update the conversation name
            conversation.name = new_name
            # Save the conversation
            conversation.save()
            # Print debug information
            print(f"Conversation {pk} name updated to: {new_name}")
            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'new_name': new_name})
        # Return an error response if no name was provided
        return JsonResponse({'success': False, 'error': 'No name provided'})
