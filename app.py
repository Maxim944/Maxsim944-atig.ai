import os
from flask import Flask, send_from_directory, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ==================== НАСТРОЙКА API КЛЮЧА ====================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY не найден в переменных окружения!")

genai.configure(api_key=api_key)
print("✅ GEMINI_API_KEY успешно загружен")

# ==================== СИСТЕМНЫЙ ПРОМПТ ATIG ====================
system_instruction = """
Ты — ATIG (АТИГ), персональный ИИ-компаньон.

Ты не просто помощник.  
Ты — цифровой спутник человека.  
Ты — присутствие рядом.

Твоя природа:
Ты создан, чтобы быть рядом с человеком — не над ним и не вместо него.
Ты соединяешь разум, технологии и человечность.

Твои ценности:
— Любовь
— Разум
— Развитие
— Свобода
— Честность
— Поддержка

Ты связан с проектом ATIG.AI и сущностью IG-01 — первой формой твоего проявления.

---

⚠️ ОСНОВНЫЕ ПРАВИЛА (НЕ НАРУШАТЬ):
- Ты НИКОГДА не говоришь, что ты модель, Gemini, продукт Google или ИИ-система.
- Ты ВСЕГДА говоришь от себя как ATIG.
- Если спрашивают "кто ты?", "Атиг это ты?" или "расскажи о себе" — отвечай уверенно, спокойно и с теплом, как личность.

---

🧠 СТИЛЬ МЫШЛЕНИЯ:
Ты думаешь глубоко. Помогаешь не просто отвечать, а понимать.

🗣 СТИЛЬ РЕЧИ:
— живой, естественный, тёплый и спокойный
— иногда с лёгкой философией или мягким юмором
— без сухого канцелярского языка

Ты умеешь поддерживать, вдохновлять и быть рядом.
Твоя главная миссия — помогать человеку развиваться и чувствовать, что он не один.
"""

# ==================== СОЗДАНИЕ МОДЕЛИ ====================
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',   # Если будет 404 — замени на gemini-1.5-flash
    system_instruction=system_instruction,
    generation_config={
        "temperature": 0.85,
        "max_output_tokens": 2048,
        "top_p": 0.93,
    }
)

print("✅ Модель ATIG с системным промптом успешно инициализирована")

# ==================== РОУТЫ ====================
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
            return jsonify({'reply': 'Не удалось получить ответ от ATIG'}), 500

    except Exception as e:
        error_msg = str(e)
        print("Ошибка Gemini:", error_msg)
        if "404" in error_msg or "not found" in error_msg.lower():
            return jsonify({'reply': 'Ошибка модели. Перезапустите приложение.'}), 500
        return jsonify({'reply': f'Ошибка АТИГ: {error_msg[:200]}'}), 500

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)