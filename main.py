import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="ATIG System Core")

# Включаем сжатие, чтобы страницы на смартфонах загружались мгновенно
app.add_middleware(GZipMiddleware, minimum_size=1000)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_file_path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)

# Конфигурация Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Внимание: GEMINI_API_KEY не задан в окружении. Бэкенд работает в режиме эхо-теста.")

# --- ЯВНЫЕ И БЕЗОПАСНЫЕ МАРШРУТЫ ДЛЯ СТРАНИЦ ---
# Это заменяет старый цикл с lambda, который вызывал путаницу в путях

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


# --- ОБРАБОТКА ДИАЛОГА (СВЯЗКА С GEMINI) ---

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Сообщение пустое")
    
    if not GEMINI_API_KEY:
        return {"response": f"[Тест] ATIG принял запрос: {request.message}"}
    
    try:
        # Используем быструю и точную модель
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Строгая системная инструкция: друг, наставник, без лишнего космического пафоса
        system_instruction = (
            "Ты — ATIG, персональный ассистент, друг, товарищ и наставник. "
            "Твой тон — серьезный, надежный, спокойный и глубокий. Отвечай емко, по делу, "
            "без лишней космической риторики, если тебя об этом прямо не просят."
        )
        
        response = model.generate_content(
            f"{system_instruction}\n\nПользователь: {request.message}"
        )
        return {"response": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Если в корне проекта будут лежать папки со стилями или картинками, 
# их можно будет безопасно раздавать через эту строчку (пока закомментирована):
# app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
