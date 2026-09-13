/**
 * ATIG Neural AI - UI Logic Module (Single Page App Edition)
 * Трансформирует стартовый экран в активный чат при отправке запроса.
 */

class ATIGUI {
  constructor() {
    this.activeModel = '✦ Qwen 2.5 Max // ATIG Core';
    this.isProcessing = false;
    this.isChatStarted = false;
    this.typingSpeed = 50;

    this.initDOM();
    this.initEvents();
  }

  initDOM() {
    this.mainContent = document.querySelector('.main-content');
    this.textarea = document.querySelector('.prompt-box textarea');
    this.sendBtn = document.querySelector('.send-btn');
    this.modelChip = document.querySelector('.model-selector-chip');
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

    // Переключаем макет в режим активного чата при первой отправке
    if (!this.isChatStarted) {
      this.switchToChatMode();
    }

    this.processQuery(text);
  }

  // Трансформирует стартовую страницу в контейнер сообщений
  switchToChatMode() {
    this.isChatStarted = true;
    this.mainContent.innerHTML = ''; // Очищаем стартовые логотип и чипсы
    
    // Настраиваем контейнер для потока сообщений
    this.mainContent.style.justifyContent = 'flex-start';
    this.mainContent.style.alignItems = 'stretch';
    this.mainContent.style.textAlign = 'left';
    this.mainContent.style.gap = '16px';
  }

  async processQuery(text) {
    // 1. Отображаем карточку пользователя
    this.appendUserCard(text);

    // 2. Статус-пилюля «Thought»
    const statusPill = this.appendStatusPill('Thought 1s');
    await this.delay(700);
    statusPill.textContent = 'Worked with Qwen Engine ∨';

    // 3. Создаем блок для ответа нейросети
    const aiResponseEl = this.appendEmptyAIResponse();

    // 4. Генерируем ответ Qwen
    const responseText = `Ядро ${this.activeModel} на связи. Запрос «${text}» успешно принят и сохранен в структуры памяти ATIG. Ожидаю следующую команду.`;

    await this.streamText(responseText, aiResponseEl);
    this.isProcessing = false;
  }

  // --- РЕНДЕРИНГ ЭЛЕМЕНТОВ ---

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

    this.mainContent.appendChild(resp);
    this.scrollToBottom();
    return resp;
  }

  streamText(text, element) {
    return new Promise((resolve) => {
      const words = text.split(' ');
      let i = 0;

      const interval = setInterval(() => {
        if (i < words.length) {
          element.innerHTML += words[i] + ' ';
          this.scrollToBottom();
          i++;
        } else {
          clearInterval(interval);
          resolve();
        }
      }, this.typingSpeed);
    });
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  scrollToBottom() {
    this.mainContent.scrollTop = this.mainContent.scrollHeight;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.atigApp = new ATIGUI();
});
