from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation_list'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('<int:pk>/new_message/', views.new_message, name='new_message'),
    path('new/', views.new_conversation, name='new_conversation'),
]
