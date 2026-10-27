import asyncio
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from sqlalchemy import select

from app.worker import celery_app
from app.db import AsyncSessionLocal
from app.models import Subscription, SubscriptionStatus, Plan, User
from app.config import settings


def _send_email_smtp(to_email: str, subject: str, body: str):
    """Вспомогательная функция для отправки письма через MailHog."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    # Подключаемся к MailHog (в Docker он будет доступен по имени "mailhog")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.send_message(msg)


async def _check_subscriptions_async():
    """Асинхронная логика проверки подписок."""
    now = datetime.now(timezone.utc)
    # Ищем окна, которые начнутся через 2 часа (плюс-минус 10 минут)
    target_time_start = now + timedelta(hours=1, minutes=50)
    target_time_end = now + timedelta(hours=2, minutes=10)

    async with AsyncSessionLocal() as db:
        # Достаём подписки, которые активны, попадают в окно времени и ещё не были отправлены
        query = (
            select(Subscription, User.email, Plan.payload)
            .join(Plan, Subscription.plan_id == Plan.id)
            .join(User, Plan.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.window_start >= target_time_start,
                Subscription.window_start <= target_time_end,
                Subscription.notified_at.is_(None)
            )
        )
        
        result = await db.execute(query)
        subscriptions = result.all()

        for sub, email, payload in subscriptions:
            try:
                # Формируем текст письма
                sport = payload.get("sport", "тренировка")
                start_time = sub.window_start.strftime("%d.%m в %H:%M")
                body = f"Привет!\n\nНапоминаем, что через 2 часа ({start_time}) у тебя запланирована {sport}.\nПогода отличная, самое время собираться!\n\nКоманда WeatherFit"
                
                # Отправляем
                _send_email_smtp(email, "Скоро тренировка! 🏃‍♂️", body)
                
                # Отмечаем в базе, что отправили
                sub.notified_at = now
                sub.status = SubscriptionStatus.NOTIFIED
                
            except Exception as e:
                print(f"Ошибка при отправке письма для {email}: {e}")

        await db.commit()


@celery_app.task(name="app.tasks.check_subscriptions")
def check_subscriptions():
    """Синхронная обертка для Celery, которая запускает асинхронный код."""
    print("Проверка подписок...")
    asyncio.run(_check_subscriptions_async())