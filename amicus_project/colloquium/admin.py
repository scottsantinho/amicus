from django.contrib import admin
from .models import Conversation, Message

# Define an inline admin class for Message model
class MessageInline(admin.TabularInline):
    # Specify the model to be used for inline admin
    model = Message
    # Set the number of extra empty forms to display
    extra = 0

# Register the Conversation model with the admin site
@admin.register(Conversation)
# Define the admin class for Conversation model
class ConversationAdmin(admin.ModelAdmin):
    # Specify the fields to be displayed in the list view
    list_display = ('id', 'user', 'name', 'created_at', 'is_active')
    # Specify the fields to be used for filtering in the admin interface
    list_filter = ('user', 'is_active')
    # Specify the fields to be used for searching in the admin interface
    search_fields = ('name', 'user__username')
    # Include the MessageInline class for inline editing of related Message objects
    inlines = [MessageInline]

# Register the Message model with the admin site
@admin.register(Message)
# Define the admin class for Message model
class MessageAdmin(admin.ModelAdmin):
    # Specify the fields to be displayed in the list view
    list_display = ('id', 'conversation', 'is_user', 'content', 'timestamp')
    # Specify the fields to be used for filtering in the admin interface
    list_filter = ('conversation', 'is_user')
    # Specify the fields to be used for searching in the admin interface
    search_fields = ('content',)
