function initializeChat() {
    const messageForm = document.querySelector('#message-form');
    const messageList = document.querySelector('#message-list');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function sendMessage(conversationId, message) {
        fetch(`/conversations/${conversationId}/send_message/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessageToConversation(data.user_message, true);
                addMessageToConversation(data.ai_message, false);
            } else {
                console.error('Failed to send message:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function addMessageToConversation(message, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`;
        messageDiv.innerHTML = `
            <div class="max-w-xs lg:max-w-md">
                <div class="text-sm font-semibold mb-1 ${isUser ? 'text-right text-blue-600' : 'text-left text-gray-600'}">
                    ${message.name}
                </div>
                <div class="p-3 rounded-lg ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-200'}">
                    <div class="text-sm">${message.content}</div>
                    <div class="text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-500'}">
                        ${message.timestamp}
                    </div>
                </div>
            </div>
        `;
        messageList.appendChild(messageDiv);
        messageList.scrollTop = messageList.scrollHeight;
    }

    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const messageInput = this.querySelector('textarea[name="content"]');
            const message = messageInput.value.trim();
            const conversationId = this.dataset.conversationId;
            if (message && conversationId) {
                sendMessage(conversationId, message);
                messageInput.value = '';
            }
        });
    }
}

// Initialize chat when the script loads
document.addEventListener('DOMContentLoaded', initializeChat);