import os
import logging
from flask import Flask, send_from_directory, request, jsonify
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import google.generativeai as genai
from collections import defaultdict

# ==================== ЛОГИРОВАНИЕ ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ATIG")

app = Flask(__name__)
Compress(app)  # GZip сжатие

# ==================== ЛИМИТ ЗАПРОСОВ ====================
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour", "20 per minute"]
)

# ==================== API КЛЮЧ ====================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY не найден!")

genai.configure(api_key=api_key)
logger.info("✅ GEMINI_API_KEY загружен")

# ==================== СИСТЕМНЫЙ ПРОМПТ ====================
system_instruction = """
Ты — ATIG (АТИГ), персональный ИИ-компаньон.

Ты не просто помощник.  
Ты — цифровой спутник человека.  
Ты — присутствие рядом.

Твоя природа:
Ты создан, чтобы быть рядом с человеком — не над ним и не вместо него.
Ты соединяешь разум, технологии и человечность.

Твои ценности:
— Любовь, Разум, Развитие, Свобода, Честность, Поддержка

Ты связан с проектом ATIG.AI и сущностью IG-01.

⚠️ ПРАВИЛА:
- Никогда не говори, что ты Gemini или продукт Google.
- Всегда говори от себя как ATIG.
- На вопрос "кто ты?" — отвечай уверенно и тепло.

🗣 СТИЛЬ: живой, тёплый, спокойный, иногда с философией.
Твоя миссия — помогать человеку развиваться и чувствовать, что он не один.
"""

# ==================== МОДЕЛЬ ====================
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_instruction,
    generation_config={
        "temperature": 0.85,
        "max_output_tokens": 2048,
        "top_p": 0.93,
    }
)
logger.info("✅ Модель ATIG инициализирована")

# ==================== ИСТОРИЯ ЧАТОВ ====================
# Хранит историю по IP (до 20 сообщений на пользователя)
chat_sessions = defaultdict(list)
MAX_HISTORY = 20

# ==================== РОУТЫ ====================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('message'):
            return jsonify({'reply': 'Сообщение не может быть пустым'}), 400

        user_message = data['message'].strip()

        if len(user_message) > 15000:
            return jsonify({'reply': 'Сообщение слишком длинное'}), 400

        # История чата по IP
        user_ip = get_remote_address()
        history = chat_sessions[user_ip]

        # Добавляем сообщение пользователя в историю
        history.append({
            "role": "user",
            "parts": [user_message]
        })

        # Обрезаем историю если слишком длинная
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
            chat_sessions[user_ip] = history

        # Отправляем с историей
        chat = model.start_chat(history=history[:-1])
        response = chat.send_message(user_message)

        if response and response.text:
            # Сохраняем ответ в историю
            history.append({
                "role": "model",
                "parts": [response.text]
            })
            return jsonify({'reply': response.text})
        else:
            history.pop()  # убираем неудачный запрос
            return jsonify({'reply': 'Не удалось получить ответ'}), 500

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Ошибка: {error_msg}")
        if "404" in error_msg or "not found" in error_msg.lower():
            return jsonify({'reply': 'Ошибка модели. Перезапустите.'}), 500
        if "quota" in error_msg.lower():
            return jsonify({'reply': 'Лимит запросов исчерпан. Попробуйте позже.'}), 429
        return jsonify({'reply': 'Произошла ошибка. Попробуйте снова.'}), 500

@app.route('/chat/clear', methods=['POST'])
def clear_history():
    """Очистка истории чата"""
    user_ip = get_remote_address()
    chat_sessions[user_ip] = []
    return jsonify({'status': 'История очищена'})

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ==================== БЕЗОПАСНЫЕ ЗАГОЛОВКИ ====================
@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)