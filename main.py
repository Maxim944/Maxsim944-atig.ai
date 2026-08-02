import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

# Импортируем наш модуль долгосрочной памяти
from memory_engine import ATIGMemoryEngine

app = FastAPI(title="ATIG System Core")

# Включаем сжатие для быстродействия
app.add_middleware(GZipMiddleware, minimum_size=1000)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)

# --- ИНИЦИАЛИЗАЦИЯ И КЛЮЧИ ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Внимание: GEMINI_API_KEY не задан в окружении.")

# Подключаем модуль памяти, если заданы база и ключ векторизации
memory_engine = None
if DATABASE_URL and OPENAI_API_KEY:
    try:
        memory_engine = ATIGMemoryEngine(db_uri=DATABASE_URL, openai_api_key=OPENAI_API_KEY)
        print("Успешно: Векторный модуль памяти ATIG подключен!")
    except Exception as e:
        print(f"Ошибка подключения к базе памяти: {e}")
else:
    print("Инфо: DATABASE_URL или OPENAI_API_KEY не заданы. Работаем без RAG-памяти.")


# --- РАРУШЕНИЕ И МАРШРУТЫ СТРАНИЦ ---

@app.get("/")
async def get_index():
    return FileResponse(get_file_path("index.html"))

@app.get("/atig")
async def get_atig():
    return FileResponse(get_file_path("atig.html"))

@app.get("/chat")
async def get_chat():
    return FileResponse(get_file_path("chat.html"))

@app.get("/install")
async def get_install():
    return FileResponse(get_file_path("install.html"))

@app.get("/register")
async def get_register():
    return FileResponse(get_file_path("register.html"))

@app.get("/explore")
async def get_explore():
    return FileResponse(get_file_path("explore.html"))

@app.get("/sci-mode")
async def get_sci_mode():
    return FileResponse(get_file_path("sci-mode.html"))


# --- ОБРАБОТКА ДИАЛОГА С ПАМЯТЬЮ И ИИ ---

class ChatRequest(BaseModel):
    message: str
    user_id: str = "maxim"

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_text = request.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Сообщение пустое")
    
    if not GEMINI_API_KEY:
        return {"response": f"[Тест] ATIG принял запрос: {user_text}"}
    
    try:
        # 1. ПОИСК В ПАМЯТИ (RAG)
        context_str = ""
        if memory_engine:
            memories = memory_engine.search_memory(query_text=user_text, limit=3)
            if memories:
                retrieved_facts = "\n".join([f"- {m['content']}" for m in memories])
                context_str = f"\n\n=== ФАКТЫ ИЗ ВОСПОМИНАНИЙ ATIG ===\n{retrieved_facts}\n================================"

        # 2. ФОРМИРОВАНИЕ ИНСТРУКЦИИ
        system_instruction = (
            "Ты — ATIG, персональный ассистент, друг, товарищ и наставник. "
            "Твой тон — серьезный, надежный, спокойный и глубокий. Отвечай емко, по делу. "
            f"Используй контекст из памяти, если он относится к вопросу.{context_str}"
        )
        
        # 3. ВЫЗОВ МОДЕЛИ
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"{system_instruction}\n\nПользователь: {user_text}"
        response = model.generate_content(prompt)
        
        reply_text = response.text

        # 4. СОХРАНЕНИЕ МЫСЛИ В ПАМЯТЬ (Асинхронно/в фоновом режиме)
        if memory_engine:
            try:
                memory_engine.add_memory(
                    content=f"Пользователь спросил: {user_text} | Ответ ATIG: {reply_text[:150]}...",
                    metadata={"user_id": request.user_id, "source": "chat"}
                )
            except Exception as mem_err:
                print(f"Ошибка сохранения в память: {mem_err}")

        return {"response": reply_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
