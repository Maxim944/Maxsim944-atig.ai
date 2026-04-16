import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Настройка Gemini через переменную окружения в Railway
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Указываем актуальную и быструю модель 1.5-flash
model = genai.GenerativeModel('models/gemini-1.5-flash')

@app.route('/')
def index():
    # Отдаем ваш файл index.html (интерфейс чата)
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'reply': 'Сообщение пустое'}), 400
            
        # Запрос к нейросети и получение ответа
        response = model.generate_content(user_message)
        
        # Возвращаем текст ответа обратно в интерфейс
        return jsonify({'reply': response.text})
    except Exception as e:
        # Если что-то пойдет не так, мы увидим текст ошибки прямо в чате
        return jsonify({'reply': f'Ошибка ATIG: {str(e)}'}), 500

@app.route('/<path:path>')
def static_files(path):
    # Позволяет серверу находить дополнительные файлы сайта
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Подхватываем порт, который выдает Railway
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
