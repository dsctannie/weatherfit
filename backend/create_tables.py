import asyncio
from app.db import engine, Base
from app import models  # Обязательно импортируем модели, чтобы SQLAlchemy их увидел

async def init_db():
    async with engine.begin() as conn:
        # Удаляем старые таблицы (если есть)
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем новые таблицы из models.py
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_db())
