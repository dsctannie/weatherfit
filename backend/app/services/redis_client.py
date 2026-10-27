import redis.asyncio as redis
from app.config import settings

# Создаём пул соединений (Connection Pool)
# Пул позволяет переиспользовать соединения, а не открывать новое на каждый запрос
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, 
    decode_responses=True  # Автоматически декодировать байты в строки (удобно для JSON)
)

def get_redis() -> redis.Redis:
    """Возвращает клиент Redis, использующий наш пул соединений."""
    return redis.Redis(connection_pool=redis_pool)