import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Использование максимально стабильной версии
 model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Добавил silent=True для надежности
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'reply': 'Системная ошибка: запрос не содержит данных'}), 400
            
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'reply': 'Сообщение пустое'}), 400
            
        # Генерация ответа
        response = model.generate_content(user_message)
        
        # Проверяем наличие текста в ответе
        if response and response.text:
            return jsonify({'reply': response.text})
        else:
            return jsonify({'reply': 'АТИГ получил пустой ответ от ядра. Попробуйте еще раз.'})

    except Exception as e:
        # Выводим ошибку именно в формате JSON
        return jsonify({'reply': f'Системная ошибка ATIG: {str(e)}'}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Railway сам назначит порт через переменную PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
