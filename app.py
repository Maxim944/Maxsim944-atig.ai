import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка API ключа
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Мы переходим на gemini-pro, так как flash выдает 404
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'reply': 'Ошибка: данные не получены'}), 400
            
        user_message = data.get('message')
        if not user_message:
            return jsonify({'reply': 'Сообщение пустое'}), 400
            
        # Запрос к нейросети
        response = model.generate_content(user_message)
        
        if response and response.text:
            return jsonify({'reply': response.text})
        else:
            return jsonify({'reply': 'АТИГ: Не удалось сформировать текст ответа.'})

    except Exception as e:
        return jsonify({'reply': f'Ошибка АТИГ: {str(e)}'}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
