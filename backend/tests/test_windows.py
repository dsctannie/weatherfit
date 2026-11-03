import pytest
from app.services.windows import calculate_score, find_windows

def test_score_perfect_weather_for_run():
    # Идеальная погода для бега: 15 градусов, ветер 2, без дождя, чистый воздух, UV 2
    score = calculate_score(temp=15, wind=2, precip=0, aqi=30, uv=2, sport="run")
    # Ожидаем максимальный балл 100
    assert score == 100.0

def test_score_bad_weather_for_run():
    # Плохая погода: жара 30, ливень (2 мм/ч), смог (AQI 150)
    score = calculate_score(temp=30, wind=2, precip=2, aqi=150, uv=2, sport="run")
    # Балл должен быть низким (меньше 50), чтобы окно отбросилось
    assert score < 50.0

def test_find_windows():
    # Тестируем поиск окон. Из 3 часов: 2 хороших, 1 плохой.
    times = ["10:00", "11:00", "12:00"]
    temps = [15.0, 16.0, 35.0]  # в 12:00 слишком жарко
    winds = [2.0, 2.0, 2.0]
    precips = [0.0, 0.0, 0.0]
    aqis = [30.0, 30.0, 30.0]
    uvs = [2.0, 2.0, 2.0]
    
    windows = find_windows(times, temps, winds, precips, aqis, uvs, "run")
    
    # Ожидаем 1 окно (с 10:00 до 11:00), так как в 12:00 жарко
    assert len(windows) == 1
    assert windows[0]["start"] == "10:00"
    assert windows[0]["end"] == "11:00"