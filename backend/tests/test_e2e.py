import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db import engine, Base
from app import models
import uuid

@pytest.mark.asyncio
async def test_full_user_scenario():
    """
    Сквозной E2E-тест (User Story 1):
    1. Пользователь регистрируется.
    2. Пользователь логинится и получает токен.
    3. Пользователь запрашивает построение плана.
    """
    
    # --- ВАЖНО: Принудительно создаем таблицы перед тестом ---
    # В облаке GitHub Actions база данных пустая, поэтому тест сам должен её подготовить
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # ---------------------------------------------------------

    # Создаем тестовый клиент, который общается с нашим приложением напрямую
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 1. Регистрация (используем рандомный email, чтобы не было ошибки 409 при повторных запусках)
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        register_data = {
            "email": test_email,
            "password": "strongpassword",
            "city": "Moscow",
            "lat": 55.75,
            "lon": 37.61
        }
        response = await ac.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201, f"Ошибка при регистрации: {response.text}"
        
        # 2. Логин
        login_data = {
            "username": test_email,
            "password": "strongpassword"
        }
        response = await ac.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200, f"Ошибка при логине: {response.text}"
        token = response.json()["access_token"]
        
        # 3. Построение плана (с использованием токена)
        headers = {"Authorization": f"Bearer {token}"}
        plan_data = {
            "sport": "run",
            "duration_min": 60,
            "sessions_per_week": 3
        }
        response = await ac.post("/api/v1/plan/", json=plan_data, headers=headers)
        
        # Если Open-Meteo доступен, ждем 201 Created. 
        # Если он упал, сервер вернет 503 (деградация). Оба варианта считаются успехом.
        assert response.status_code in [201, 503], f"Ошибка при построении плана: {response.text}"
        
        if response.status_code == 201:
            data = response.json()
            assert "payload" in data
            assert "windows" in data["payload"]