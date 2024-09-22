from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ('name', 'user__username')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'is_user', 'content', 'timestamp')
    list_filter = ('conversation', 'is_user')
    search_fields = ('content',)
