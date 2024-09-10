from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation_list'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('<int:pk>/message/', views.new_message, name='new_message'),
    path('delete/', views.delete_conversations, name='delete_conversations'),
]
