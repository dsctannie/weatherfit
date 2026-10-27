from typing import Annotated, List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import User, Plan
from app.schemas import PlanRequest, PlanResponse
from app.services.weather import get_forecast, get_air_quality
from app.services.windows import find_windows, distribute_week

router = APIRouter()


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def build_plan(
    request: PlanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Строит персональный план тренировок на неделю."""
    
    # 1. Получаем погоду и качество воздуха (параллельно)
    # Возвращают кортеж: (данные, is_stale)
    forecast_data, forecast_stale = await get_forecast(current_user.lat, current_user.lon)
    air_data, air_stale = await get_air_quality(current_user.lat, current_user.lon)

    # 2. Проверяем на деградацию
    degraded = False
    degraded_reason = None

    if forecast_data is None and air_data is None:
        # Оба источника упали — отдаём ошибку 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервисы погоды временно недоступны. Попробуйте позже."
        )
    
    if air_data is None:
        degraded = True
        degraded_reason = "Air Quality API недоступен, AQI и UV не учитывались"

    # 3. Извлекаем данные в удобные списки
    # Open-Meteo возвращает вложенный словарь {"hourly": {"time": [...], "temperature_2m": [...]}}
    times = forecast_data["hourly"]["time"]
    temps = forecast_data["hourly"]["temperature_2m"]
    winds = forecast_data["hourly"]["wind_speed_10m"]
    precips = forecast_data["hourly"]["precipitation"]

    # Если air_data есть — берём AQI и UV, иначе списки из None
    if air_data:
        aqis = air_data["hourly"]["us_aqi"]
        uvs = air_data["hourly"]["uv_index"]
    else:
        aqis = [None] * len(times)
        uvs = [None] * len(times)

    # 4. Запускаем бизнес-логику
    all_windows = find_windows(times, temps, winds, precips, aqis, uvs, request.sport.value)
    best_windows = distribute_week(all_windows, request.sessions_per_week)

    # 5. Формируем итоговый JSON для сохранения в БД
    payload = {
        "sport": request.sport.value,
        "duration_min": request.duration_min,
        "sessions_per_week": request.sessions_per_week,
        "windows": best_windows,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    # 6. Сохраняем в базу данных
    new_plan = Plan(
        user_id=current_user.id,
        payload=payload,
        degraded=degraded,
        degraded_reason=degraded_reason
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)

    # 7. Возвращаем ответ
    return new_plan