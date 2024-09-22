from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation_list'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),
    path('<int:pk>/new_message/', views.new_message, name='new_message'),  # Update this line
    path('delete/', views.delete_conversations, name='delete_conversations'),
    path('<int:conversation_id>/send_message/', views.send_message, name='send_message'),  # Add this line
]
