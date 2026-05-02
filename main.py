from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def file(path):
    return os.path.join(BASE_DIR, path)

@app.get("/")
def home():
    return FileResponse(file("index.html"))

@app.get("/atig")
def atig_page():
    return FileResponse(file("atig.html"))

@app.get("/chat")
def chat_page():
    return FileResponse(file("chat.html"))

@app.get("/install")
def install_page():
    return FileResponse(file("install.html"))