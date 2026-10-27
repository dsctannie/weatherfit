from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models import Sport, SubscriptionStatus


# ==========================================
# Схемы для аутентификации (Auth)
# ==========================================

class UserRegister(BaseModel):
    """Что присылает пользователь при регистрации."""
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    city: str = Field(min_length=1, max_length=100)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class UserLogin(BaseModel):
    """Что присылает пользователь при входе."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Что возвращает сервер после успешного входа."""
    access_token: str
    token_type: str = "bearer"


# ==========================================
# Схемы для профиля (User)
# ==========================================

class UserRead(BaseModel):
    """Что сервер возвращает клиенту (БЕЗ пароля!)."""
    id: UUID
    email: EmailStr
    city: str
    lat: float
    lon: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Что можно обновить в профиле."""
    city: str | None = None
    temp_min: float | None = None
    temp_max: float | None = None


# ==========================================
# Схемы для плана (Plan)
# ==========================================

class PlanRequest(BaseModel):
    """Что присылает пользователь, чтобы построить план."""
    sport: Sport
    duration_min: int = Field(ge=15, le=240)
    sessions_per_week: int = Field(ge=1, le=7)


class PlanResponse(BaseModel):
    """Что сервер возвращает — готовый план."""
    id: UUID
    payload: dict
    degraded: bool
    degraded_reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Схемы для тренировок (Workout)
# ==========================================

class WorkoutCreate(BaseModel):
    """Что присылает пользователь, чтобы отметить тренировку."""
    sport: Sport
    started_at: datetime
    duration_min: int = Field(ge=1, le=600)


class WorkoutRead(BaseModel):
    """Что сервер возвращает в истории."""
    id: UUID
    sport: Sport
    started_at: datetime
    duration_min: int
    weather_snapshot: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Схемы для подписок (Subscription)
# ==========================================

class SubscriptionCreate(BaseModel):
    """Что присылает пользователь, чтобы подписаться на окно."""
    plan_id: UUID
    window_index: int
    window_start: datetime
    window_end: datetime


class SubscriptionRead(BaseModel):
    """Что сервер возвращает в списке подписок."""
    id: UUID
    plan_id: UUID
    window_start: datetime
    window_end: datetime
    status: SubscriptionStatus

    model_config = ConfigDict(from_attributes=True)