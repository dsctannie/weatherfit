import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, plan

# 1. Настройка логирования в STDOUT (как требует препод)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# 2. Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    description="Сервис построения плана уличных тренировок",
    version="1.0.0"
)

# 3. Настройка CORS (чтобы React с другого порта мог делать запросы)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(plan.router, prefix="/api/v1/plan", tags=["Plan"])


# 5. Базовые эндпоинты для проверки работоспособности
@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# 6. Событие при старте приложения
@app.on_event("startup")
async def startup_event():
    logger.info("Приложение WeatherFit запущено")