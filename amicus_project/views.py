from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import AIProfile, Conversation, Message
import json

@require_POST
@csrf_protect
def send_message(request):
    data = json.loads(request.body)
    user_message = data.get('message')
    
    # Save the user message to the database
    conversation, created = Conversation.objects.get_or_create(user=request.user)
    user_msg = Message.objects.create(conversation=conversation, content=user_message, is_user=True)
    
    # Generate AI response
    ai_response = generate_ai_response(user_message)
    
    # Save the AI response to the database
    ai_msg = Message.objects.create(conversation=conversation, content=ai_response, is_user=False)
    
    return JsonResponse({
        'user_message': {
            'content': user_msg.content,
            'timestamp': user_msg.timestamp.strftime("%B %d, %Y %H:%M"),
            'is_user': True
        },
        'ai_response': {
            'content': ai_msg.content,
            'timestamp': ai_msg.timestamp.strftime("%B %d, %Y %H:%M"),
            'is_user': False
        }
    })

def chat_view(request):
    conversation, created = Conversation.objects.get_or_create(user=request.user)
    messages = conversation.messages.all().order_by('timestamp')
    
    ai_profile = AIProfile.objects.first()
    ai_name = ai_profile.ai_name if ai_profile else "AI Assistant"
    
    context = {
        'messages': messages,
        'ai_name': ai_name,
    }
    
    return render(request, 'colloquium/chat.html', context)

def generate_ai_response(user_message):
    # Your AI logic here
    return "This is a placeholder AI response."