/**
 * ATIG Neural AI - UI & Ollama Integration Module
 * Связывает интерфейс сайта с локальной нейросетью Qwen в Termux.
 */

class ATIGUI {
  constructor() {
    this.modelName = 'qwen2.5-coder:1.5b'; // Модель из Termux
    this.isProcessing = false;
    this.isChatStarted = false;

    this.initDOM();
    this.initEvents();
  }

  initDOM() {
    this.mainContent = document.querySelector('.main-content');
    this.textarea = document.querySelector('.prompt-box textarea');
    this.sendBtn = document.querySelector('.send-btn');
    this.chipBtns = document.querySelectorAll('.chip-btn');
  }

  initEvents() {
    if (this.textarea) {
      this.textarea.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    if (this.sendBtn) {
      this.sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleSubmit();
      });
    }

    if (this.chipBtns) {
      this.chipBtns.forEach(chip => {
        chip.addEventListener('click', () => {
          if (this.textarea) {
            this.textarea.value = chip.textContent.replace(/^[✦🧬⚡]\s*/, '');
            this.textarea.focus();
          }
        });
      });
    }
  }

  handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.handleSubmit();
    }
  }

  handleSubmit() {
    const text = this.textarea.value.trim();
    if (!text || this.isProcessing) return;

    this.isProcessing = true;
    this.textarea.value = '';

    if (!this.isChatStarted) {
      this.switchToChatMode();
    }

    this.processQuery(text);
  }

  switchToChatMode() {
    this.isChatStarted = true;
    this.mainContent.innerHTML = '';
    this.mainContent.style.justifyContent = 'flex-start';
    this.mainContent.style.alignItems = 'stretch';
    this.mainContent.style.textAlign = 'left';
    this.mainContent.style.gap = '16px';
  }

  async processQuery(text) {
    this.appendUserCard(text);

    const statusPill = this.appendStatusPill('Запрос к Qwen...');
    const aiResponseEl = this.appendEmptyAIResponse();

    try {
      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: this.modelName,
          messages: [{ role: 'user', content: text }],
          stream: true
        })
      });

      if (!response.ok) throw new Error('Ollama API error');

      statusPill.textContent = `Ядро: ${this.modelName} ∨`;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.trim() !== '') {
            try {
              const parsed = JSON.parse(line);
              if (parsed.message && parsed.message.content) {
                aiResponseEl.textContent += parsed.message.content;
                this.scrollToBottom();
              }
            } catch (e) {
              // Пропускаем фрагменты неполных чанков
            }
          }
        }
      }
    } catch (err) {
      statusPill.textContent = 'Ошибка связи с Ollama ✕';
      statusPill.style.background = 'rgba(239, 68, 68, 0.1)';
      statusPill.style.color = '#f87171';
      aiResponseEl.innerHTML = '<span style="color: #ef4444;">Не удалось подключиться к Ollama. Проверьте запуск сервера в Termux.</span>';
    } finally {
      this.isProcessing = false;
    }
  }

  appendUserCard(text) {
    const card = document.createElement('div');
    card.style.background = 'rgba(255, 255, 255, 0.08)';
    card.style.border = '1px solid rgba(255, 255, 255, 0.12)';
    card.style.padding = '12px 16px';
    card.style.borderRadius = '16px';
    card.style.maxWidth = '85%';
    card.style.alignSelf = 'flex-end';
    card.style.color = '#ffffff';
    card.style.fontSize = '0.95rem';
    card.style.wordBreak = 'break-word';
    card.textContent = text;

    this.mainContent.appendChild(card);
    this.scrollToBottom();
  }

  appendStatusPill(text) {
    const pill = document.createElement('div');
    pill.style.fontSize = '0.78rem';
    pill.style.color = 'var(--gold-light)';
    pill.style.background = 'rgba(212, 175, 55, 0.1)';
    pill.style.border = '1px solid var(--panel-border)';
    pill.style.padding = '4px 10px';
    pill.style.borderRadius = '12px';
    pill.style.width = 'fit-content';
    pill.style.fontFamily = "'Fira Code', monospace";
    pill.textContent = text;

    this.mainContent.appendChild(pill);
    this.scrollToBottom();
    return pill;
  }

  appendEmptyAIResponse() {
    const resp = document.createElement('div');
    resp.style.color = 'var(--text-main)';
    resp.style.fontSize = '0.95rem';
    resp.style.lineHeight = '1.5';
    resp.style.padding = '4px 8px';
    resp.style.maxWidth = '90%';
    resp.style.whiteSpace = 'pre-wrap';

    this.mainContent.appendChild(resp);
    this.scrollToBottom();
    return resp;
  }

  scrollToBottom() {
    this.mainContent.scrollTop = this.mainContent.scrollHeight;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.atigApp = new ATIGUI();
});
