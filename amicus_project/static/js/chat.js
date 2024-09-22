async function sendMessage() {
    const messageInput = document.querySelector('#message-input');
    const messageContent = messageInput.value.trim();

    if (messageContent) {
        messageInput.value = '';

        try {
            const response = await fetch('/send_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ message: messageContent }),
            });

            if (response.ok) {
                const data = await response.json();
                addMessageToChat(data.user_message);
                addMessageToChat(data.ai_response);
            } else {
                console.error('Failed to send message');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

function addMessageToChat(message) {
    const chatWindow = document.querySelector('#chat-window');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${message.is_user ? 'justify-end' : 'justify-start'} mb-4`;

    const currentUserName = document.querySelector('#current-user-name').textContent;
    const aiName = document.querySelector('#ai-name').textContent;

    messageDiv.innerHTML = `
        <div class="max-w-xs lg:max-w-md">
            <div class="text-sm font-semibold mb-1 ${message.is_user ? 'text-right text-blue-600' : 'text-left text-gray-600'}">
                <span class="sender-name">${message.is_user ? currentUserName : aiName}</span>
            </div>
            <div class="p-3 rounded-lg ${message.is_user ? 'bg-blue-500 text-white' : 'bg-gray-200'}">
                <div class="text-sm message-content">${message.content}</div>
                <div class="text-xs mt-1 ${message.is_user ? 'text-blue-200' : 'text-gray-500'} message-timestamp">${message.timestamp}</div>
            </div>
        </div>
    `;

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

document.querySelector('#send-button').addEventListener('click', sendMessage);
document.querySelector('#message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});