from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


# 1. Движок (engine) — управляет соединениями с базой
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG  # Если DEBUG=true, все SQL-запросы будут видны в консоли
)

# 2. Фабрика сессий — создаёт сессии для каждого запроса
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Не "забывать" данные после сохранения
)

# 3. Базовый класс для моделей (таблиц)
class Base(DeclarativeBase):
    pass

# 4. Зависимость (dependency) для FastAPI
async def get_db():
    """Выдаёт сессию БД, а после запроса автоматически её закрывает."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()