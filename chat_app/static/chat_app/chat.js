(function () {
  const chatForm = document.getElementById('chat-form');
  const chatLog = document.getElementById('chat-log');
  const input = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');

  function getCookie(name) {
    const cookieValue = document.cookie
      .split('; ')
      .find((row) => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
  }

  function renderMessage(role, content) {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.remove();

    const wrapper = document.createElement('div');
    wrapper.className = `d-flex mb-3 ${role === 'user' ? 'justify-content-end' : 'justify-content-start'}`;

    const bubble = document.createElement('div');
    bubble.className = `msg-bubble ${role === 'user' ? 'msg-user' : 'msg-ai'}`;

    const roleLabel = document.createElement('div');
    roleLabel.className = 'msg-role small text-muted mb-1';
    roleLabel.textContent = role === 'user' ? 'Вы' : 'AI';

    const contentEl = document.createElement('div');
    contentEl.className = 'msg-content';
    contentEl.textContent = content;

    bubble.appendChild(roleLabel);
    bubble.appendChild(contentEl);
    wrapper.appendChild(bubble);
    chatLog.appendChild(wrapper);

    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function autoResize() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  }

  input.addEventListener('input', autoResize);

  chatForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    renderMessage('user', message);
    input.value = '';
    autoResize();
    sendBtn.disabled = true;

    try {
      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();
      if (!response.ok) {
        renderMessage('ai', data.error || 'Ошибка запроса.');
      } else {
        renderMessage('ai', data.ai.content);
      }
    } catch (error) {
      renderMessage('ai', 'Сетевая ошибка при запросе к серверу.');
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  });

  autoResize();
  chatLog.scrollTop = chatLog.scrollHeight;
})();
