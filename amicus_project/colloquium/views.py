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
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')

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
    # Get the conversation or return 404 if not found
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    # Check if the request method is POST
    if request.method == 'POST':
        # Create a form instance with POST data
        form = MessageForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Create a new message instance but don't save to database yet
            message = form.save(commit=False)
            # Set the conversation for the message
            message.conversation = conversation
            # Set is_user to True as this is a user message
            message.is_user = True
            # Save the message to the database
            message.save()
            # Create a dummy AI response (placeholder for actual AI logic)
            Message.objects.create(
                conversation=conversation,
                content="This is a dummy AI response.",
                is_user=False
            )
            # Save the conversation to update the 'updated_at' field
            conversation.save()
            # Redirect to the conversation detail page
            return redirect('conversation_detail', pk=pk)
    # If not POST request, redirect to conversation detail page
    return redirect('conversation_detail', pk=pk)

# Define a view for creating a new conversation, requiring login
@login_required
def new_conversation(request):
    # Create a new conversation for the current user
    conversation = Conversation.objects.create(user=request.user)
    # Redirect to the detail page of the newly created conversation
    return redirect('conversation_detail', pk=conversation.pk)
