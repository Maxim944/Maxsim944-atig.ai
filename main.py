import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def file(path: str) -> str:
    return os.path.join(BASE_DIR, path)

# Статические файлы (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

# Маршруты страниц
ROUTES = {
    "/": "index.html",
    "/atig": "atig.html",
    "/chat": "chat.html",
    "/install": "install.html",
    "/register": "register.html",
    "/explore": "explore.html",
    "/sci-mode": "sci-mode.html",
}

for route, html in ROUTES.items():
    app.add_api_route(
        route,
        lambda f=html: FileResponse(file(f)),
        methods=["GET"]
    )