from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Создаём приложение Celery
# В качестве брокера (очереди задач) и хранилища результатов используем Redis
celery_app = Celery(
    "weatherfit",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Настройка расписания (Celery Beat)
celery_app.conf.beat_schedule = {
    "check-subscriptions-every-10-mins": {
        "task": "app.tasks.check_subscriptions",
        # 600 секунд = 10 минут
        "schedule": 600.0,
    },
}