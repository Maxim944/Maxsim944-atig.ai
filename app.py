import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Использование максимально стабильной версии
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'reply': 'Сообщение пустое'}), 400
            
        # Генерация ответа
        response = model.generate_content(user_message)
        
        # Важно: берем именно текст
        answer = response.text if response.text else "ИИ не смог сформировать ответ."
        return jsonify({'reply': answer})

    except Exception as e:
        # Выводим ошибку для диагностики
        return jsonify({'reply': f'Системная ошибка ATIG: {str(e)}'}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
