from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.routers import router

app = FastAPI(title="AnimeHako API", description="API для каталога аниме", version="1.0.0")

# Монтируем статические файлы для раздачи изображений
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "AnimeHako API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}