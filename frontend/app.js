document.addEventListener('DOMContentLoaded', () => {
    const rawApiBase = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) || '';
    const API_BASE_URL = rawApiBase.replace(/\/+$/, '');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const exampleQuestions = document.querySelectorAll('.example-btn');
    const exampleQuestionsContainer = document.getElementById('example-questions');

    // Format text into basic HTML paragraphs
    const formatMessage = (text) => {
        return text.split('\n\n').map(p => `<p>${p}</p>`).join('');
    };

    const appendMessage = (text, sender, isHtml = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble');
        
        if (isHtml) {
            bubble.innerHTML = text;
        } else {
            bubble.textContent = text;
        }
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    const appendBotResponse = (data) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        
        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble');
        
        // Add answer text
        bubble.innerHTML = formatMessage(data.answer);
        
        // Add citation if available
        if (data.citation_url) {
            const citationDiv = document.createElement('div');
            citationDiv.classList.add('citation');
            
            const link = document.createElement('a');
            link.href = data.citation_url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.classList.add('citation-link');
            
            // Extract domain and path for cleaner display
            try {
                const urlObj = new URL(data.citation_url);
                link.textContent = 'View on Groww ↗';
            } catch (e) {
                link.textContent = data.citation_url;
            }
            
            citationDiv.appendChild(link);
            
            // Note: Since API might not return footer directly as a distinct field if we embedded it in answer,
            // we will parse or rely on the backend. Oh wait, backend currently returns answer, citation_url, route.
            // If the backend `answer` includes the "Last updated" footer as text, it's already rendered above.
            // But we can style the citation block nicely.
            
            bubble.appendChild(citationDiv);
        }
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    const showLoading = () => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        messageDiv.id = 'loading-indicator';
        
        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble', 'typing-indicator');
        
        bubble.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    const removeLoading = () => {
        const loading = document.getElementById('loading-indicator');
        if (loading) loading.remove();
    };

    const scrollToBottom = () => {
        chatMessages.parentElement.scrollTop = chatMessages.parentElement.scrollHeight;
    };

    const handleSend = async (message) => {
        if (!message.trim()) return;
        
        // Hide example questions if they are still visible
        if (exampleQuestionsContainer && exampleQuestionsContainer.style.display !== 'none') {
            exampleQuestionsContainer.style.display = 'none';
        }

        // Add user message
        appendMessage(message, 'user');
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        
        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();
            removeLoading();
            appendBotResponse(data);

        } catch (error) {
            console.error('Error:', error);
            removeLoading();
            appendMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    };

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        handleSend(chatInput.value);
    });

    exampleQuestions.forEach(btn => {
        btn.addEventListener('click', () => {
            handleSend(btn.textContent);
        });
    });
});
