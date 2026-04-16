import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# === Рекомендуемые настройки ===
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',   # или 'gemini-2.5-pro'
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "top_p": 0.95,
        "top_k": 40,
    },
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('message'):
            return jsonify({'reply': 'Сообщение не может быть пустым'}), 400

        user_message = data['message'].strip()
        
        # Защита от слишком длинных сообщений
        if len(user_message) > 10000:
            return jsonify({'reply': 'Сообщение слишком длинное'}), 400

        response = model.generate_content(user_message)
        
        if response and hasattr(response, 'text') and response.text:
            return jsonify({'reply': response.text})
        else:
            return jsonify({'reply': 'Не удалось получить ответ от АТИГ.'}), 500

    except Exception as e:
        error_str = str(e)
        print(f"Ошибка Gemini: {error_str}")  # для логов
        return jsonify({
            'reply': f'Ошибка АТИГ: {error_str[:200]}'
        }), 500

# Отдача статических файлов (index.html, css, js и т.д.)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False на продакшене