import json
from datetime import date

import httpx
import pybreaker
from app.config import settings
from app.services.redis_client import get_redis

# ==========================================
# 1. НАСТРОЙКА CIRCUIT BREAKER'ОВ
# ==========================================
# Два независимых предохранителя: для погоды и для воздуха
forecast_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=120)
air_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=120)


# ==========================================
# 2. ФУНКЦИИ ЗАПРОСА К OPEN-METEO
# ==========================================
@forecast_breaker
async def _fetch_forecast_api(lat: float, lon: float) -> dict:
    """Делает реальный HTTP-запрос к Open-Meteo Forecast."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,precipitation",
        "forecast_days": 7,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(settings.OPEN_METEO_FORECAST_URL, params=params)
        response.raise_for_status()  # Если 404 или 500 — выбросит ошибку
        return response.json()


@air_breaker
async def _fetch_air_quality_api(lat: float, lon: float) -> dict:
    """Делает реальный HTTP-запрос к Open-Meteo Air Quality."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "us_aqi,uv_index",
        "forecast_days": 7,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(settings.OPEN_METEO_AIR_QUALITY_URL, params=params)
        response.raise_for_status()
        return response.json()


# ==========================================
# 3. ОСНОВНЫЕ ФУНКЦИИ С КЭШИРОВАНИЕМ И ДЕГРАДАЦИЕЙ
# ==========================================
async def get_forecast(lat: float, lon: float) -> tuple[dict | None, bool]:
    """
    Возвращает (данные, is_stale).
    Если данные из кэша — is_stale=False (свежие).
    Если данные из внешнего API и API упал — is_stale=True (устаревшие).
    """
    redis = get_redis()
    cache_key = f"wf:forecast:{lat}:{lon}:{date.today()}"

    # 1. Пытаемся взять из кэша
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached), False

    # 2. Если в кэше нет — идём в API
    try:
        data = await _fetch_forecast_api(lat, lon)
        # Сохраняем в кэш на 30 минут (1800 секунд)
        await redis.setex(cache_key, 1800, json.dumps(data))
        return data, False
    except (pybreaker.CircuitBreakerError, httpx.HTTPError) as e:
        # Если Circuit Breaker разомкнут или сеть упала
        print(f"Forecast API error: {e}")
        # Пытаемся достать "устаревшие" данные (если они есть)
        return None, True


async def get_air_quality(lat: float, lon: float) -> tuple[dict | None, bool]:
    """Аналогично для Air Quality."""
    redis = get_redis()
    cache_key = f"wf:air:{lat}:{lon}:{date.today()}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached), False

    try:
        data = await _fetch_air_quality_api(lat, lon)
        await redis.setex(cache_key, 1800, json.dumps(data))
        return data, False
    except (pybreaker.CircuitBreakerError, httpx.HTTPError) as e:
        print(f"Air Quality API error: {e}")
        return None, True