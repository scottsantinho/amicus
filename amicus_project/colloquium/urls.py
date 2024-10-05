from django.urls import path
from . import views

# Define URL patterns for the colloquium app
urlpatterns = [
    # Map the root URL to the ConversationListView
    # This view displays a list of all conversations
    path('', views.ConversationListView.as_view(), name='conversation_list'),
    
    # Map the 'new/' URL to the new_conversation view
    # This view handles the creation of a new conversation
    path('new/', views.new_conversation, name='new_conversation'),
    
    # Map URLs with conversation IDs to the ConversationDetailView
    # This view displays details of a specific conversation
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    
    # Map URLs for deleting a specific conversation
    # This view handles the deletion of a conversation
    path('<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # Map URLs for adding a new message to a specific conversation
    # This view handles the addition of a new message
    path('<int:pk>/new_message/', views.new_message, name='new_message'),
    
    # Map the 'delete/' URL to the delete_conversations view
    # This view handles the deletion of multiple conversations
    path('delete/', views.delete_conversations, name='delete_conversations'),
    
    # Map URLs for sending a message in a specific conversation
    # This view handles sending a message
    path('<int:conversation_id>/send_message/', views.send_message, name='send_message'),
    
    # Map URLs for editing a specific conversation
    # This view handles the editing of a conversation
    path('<int:pk>/edit/', views.ConversationEditView.as_view(), name='conversation_edit'),
]
