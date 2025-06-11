class ChatWindow {
  constructor(formId, messagesId) {
    this.form = document.getElementById(formId);
    this.messagesContainer = document.getElementById(messagesId);
    this.endpoint = this.form.dataset.endpoint;

    this.form.addEventListener('submit', e => {
      e.preventDefault();
      const input = this.form.querySelector('input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      this.addMessage(text, 'user');
      this.sendToServer(text);
    });
  }

  addMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.textContent = text;
    this.messagesContainer.append(div);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  async sendToServer(text) {
    try {
      const resp = await fetch(this.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await resp.json();
      this.addMessage(data.response, 'assistant');
    } catch (err) {
      this.addMessage('Ошибка сети или сервера', 'assistant');
      console.error(err);
    }
  }
}

// Инициализация двух окон
window.addEventListener('DOMContentLoaded', () => {
  new ChatWindow('form-clair', 'messages-clair');
  new ChatWindow('form-obscur', 'messages-obscur');
});
