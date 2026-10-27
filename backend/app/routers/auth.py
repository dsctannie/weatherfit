from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.db import get_db
from app.models import User
from app.schemas import Token, UserRead, UserRegister

# Создаём роутер. Все пути внутри него будут начинаться с префикса /api/v1/auth
router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Регистрация нового пользователя."""
    # 1. Проверяем, существует ли уже пользователь с таким email
    existing_user = await db.execute(select(User).where(User.email == user_in.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )

    # 2. Создаём нового пользователя
    new_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        city=user_in.city,
        lat=user_in.lat,
        lon=user_in.lon
    )
    
    # 3. Сохраняем в базу
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Обновляем объект, чтобы получить id и created_at из БД

    # 4. Сразу выдаём токен, чтобы пользователю не пришлось логиниться заново
    access_token = create_access_token(subject=new_user.id)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Вход в систему (получение токена)."""
    # 1. Ищем пользователя по email (в форме логина он называется username)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # 2. Проверяем пароль. Если пользователя нет или пароль не совпал — ошибка
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Выдаём токен
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Получить профиль текущего авторизованного пользователя."""
    return current_user