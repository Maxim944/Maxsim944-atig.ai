import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка Gemini через переменную, которую вы уже ввели в Railway
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    # Отдаем ваш файл index.html
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'reply': 'Сообщение пустое'}), 400
            
        # Запрос к нейросети Gemini
        response = model.generate_content(user_message)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f'Ошибка ATIG: {str(e)}'}), 500

@app.route('/<path:path>')
def static_files(path):
    # Позволяет серверу находить другие файлы (стили, скрипты, картинки)
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Railway автоматически выдает порт, мы его подхватываем
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
