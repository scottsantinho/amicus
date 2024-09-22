from django.urls import path
from . import views
from colloquium.views import ConversationEditView

urlpatterns = [
    # ... other url patterns ...
    path('send_message/', views.send_message, name='send_message'),
    path('conversation/<int:pk>/edit/', ConversationEditView.as_view(), name='conversation_edit'),
]