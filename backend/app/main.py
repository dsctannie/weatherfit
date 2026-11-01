import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, plan
from app.db import engine, Base
from app import models  # Обязательно для создания таблиц

# 1. Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# 2. Создаем таблицы при старте
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск сервера. Проверка таблиц БД...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы успешно проверены/созданы")
    yield
    logger.info("Сервер остановлен")

# 3. Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис построения плана уличных тренировок",
    version="1.0.0",
    lifespan=lifespan
)

# 4. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(plan.router, prefix="/api/v1/plan", tags=["Plan"])

# 6. Проверка здоровья
@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
