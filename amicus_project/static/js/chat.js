function initializeChat() {
    const messageForm = document.querySelector('#message-form');
    const messageList = document.querySelector('#message-list');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function sendMessage(conversationId, message) {
        // Immediately display user message
        const userMessage = {
            name: document.getElementById('current-user-name').textContent.trim(),
            content: message,
            timestamp: new Date().toLocaleString()
        };
        addMessageToConversation(userMessage, true);

        // Display AI typing indicator
        const aiName = document.getElementById('ai-name').textContent.trim();
        const typingIndicator = addTypingIndicator(aiName);

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
                // Remove typing indicator
                typingIndicator.remove();
                // Add AI message
                addMessageToConversation(data.ai_message, false);
            } else {
                console.error('Failed to send message:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.remove();
        });
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

    function addTypingIndicator(aiName) {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex justify-start mb-4';
        typingDiv.innerHTML = `
            <div class="max-w-xs lg:max-w-md">
                <div class="text-sm font-semibold mb-1 text-left text-gray-600">
                    ${aiName}
                </div>
                <div class="p-3 rounded-lg bg-gray-200">
                    <div class="text-sm typing-indicator">${aiName} is typing<span class="dots">...</span></div>
                </div>
            </div>
        `;
        messageList.appendChild(typingDiv);
        messageList.scrollTop = messageList.scrollHeight;
        animateTypingIndicator(typingDiv.querySelector('.dots'));
        return typingDiv;
    }

    function animateTypingIndicator(dotsElement) {
        let dotCount = 0;
        const interval = setInterval(() => {
            dotCount = (dotCount + 1) % 4;
            dotsElement.textContent = '.'.repeat(dotCount);
        }, 500);
        dotsElement.dataset.interval = interval;
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