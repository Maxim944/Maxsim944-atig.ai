import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Актуальная модель
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config={
        "temperature": 0.7,
        "max_output_tokens": 2048,
    }
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
        
        if len(user_message) > 15000:
            return jsonify({'reply': 'Сообщение слишком длинное'}), 400

        response = model.generate_content(user_message)
        
        if response and response.text:
            return jsonify({'reply': response.text})
        else:
            return jsonify({'reply': 'Не удалось получить ответ'}), 500

    except Exception as e:
        error_msg = str(e)
        print("Ошибка Gemini:", error_msg)   # для логов на Railway
        if "404" in error_msg or "not found" in error_msg.lower():
            return jsonify({'reply': 'Ошибка: Модель не найдена. Перезапустите приложение.'}), 500
        return jsonify({'reply': f'Ошибка АТИГ: {error_msg[:250]}'}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)