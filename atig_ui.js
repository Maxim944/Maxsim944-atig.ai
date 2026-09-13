/**
 * ATIG Neural AI - UI Logic Module
 * Управляет интерактивностью стартовой страницы.
 */

class ATIGUI {
  constructor(config = {}) {
    // Получаем DOM-элементы
    this.textarea = document.querySelector('.prompt-box textarea');
    this.sendBtn = document.querySelector('.send-btn');
    this.modelChip = document.querySelector('.model-selector-chip');
    this.chipBtns = document.querySelectorAll('.chip-btn');
    this.form = document.querySelector('.prompt-box');

    // Состояние приложения
    this.isProcessing = false;

    // Инициализация событий
    this.initEvents();
  }

  initEvents() {
    if (this.textarea) {
      // Обработка клавиши Enter для отправки (без Shift)
      this.textarea.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    if (this.sendBtn) {
      this.sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleInputSubmit();
      });
    }

    // Обработка клика по чипсам-подсказкам
    if (this.chipBtns) {
      this.chipBtns.forEach(chip => {
        chip.addEventListener('click', () => {
          this.textarea.value = chip.textContent;
          this.textarea.focus();
        });
      });
    }
  }

  handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.handleInputSubmit();
    }
  }

  handleInputSubmit() {
    const text = this.textarea.value.trim();
    if (text && !this.isProcessing) {
      this.isProcessing = true;
      this.textarea.disabled = true; // Блокируем ввод при "отправке"
      
      // Имитация действия: перенаправление на чат-интерфейс
      this.simulateAgentAction(text);
    }
  }

  simulateAgentAction(text) {
    // В реальной системе это бы вызвало переход на другую страницу или открытие чата.
    // Мы симулируем это, добавляя запрос в URL и перенаправляя на несуществующую пока 'chat.html'.
    // В будущем мы создадим эту страницу.
    this.clearInput();
    window.location.href = `chat.html?q=${encodeURIComponent(text)}`;
  }

  clearInput() {
    this.textarea.value = '';
    this.textarea.disabled = false;
    this.textarea.rows = 1; // Сброс высоты если была авто-регулировка
    this.isProcessing = false;
  }
}

// Инициализация логики при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  window.atigApp = new ATIGUI();
});
