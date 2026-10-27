from typing import List, Dict, Any, Optional

# ==========================================
# 1. ПРАВИЛА КОМФОРТА (Правило 1 из README)
# ==========================================
SPORT_RULES = {
    "run":     {"t_min": 5,  "t_max": 25, "wind_max": 8,  "precip_max": 0.5, "aqi_max": 100, "uv_max": 7},
    "bike":    {"t_min": 10, "t_max": 28, "wind_max": 10, "precip_max": 0.2, "aqi_max": 100, "uv_max": 8},
    "workout": {"t_min": 10, "t_max": 30, "wind_max": 12, "precip_max": 0.0, "aqi_max": 120, "uv_max": 9},
}


# ==========================================
# 2. РАСЧЁТ SCORE (Правило 2 из README)
# ==========================================
def calculate_score(
    temp: float, 
    wind: float, 
    precip: float, 
    aqi: Optional[float], 
    uv: Optional[float], 
    sport: str
) -> float:
    """
    Считает оценку часа от 0 до 100.
    Если aqi или uv равны None (деградация), штрафы за них не считаются.
    """
    rules = SPORT_RULES.get(sport, SPORT_RULES["run"])
    score = 100.0

    # Штраф за температуру
    if temp < rules["t_min"]:
        score -= 10 * (rules["t_min"] - temp)
    elif temp > rules["t_max"]:
        score -= 10 * (temp - rules["t_max"])

    # Штраф за ветер
    if wind > rules["wind_max"]:
        score -= 5 * (wind - rules["wind_max"])

    # Штраф за осадки
    if precip > rules["precip_max"]:
        score -= 20 * (precip - rules["precip_max"])

    # Штраф за качество воздуха (AQI)
    if aqi is not None and aqi > rules["aqi_max"]:
        score -= 15 * (aqi - rules["aqi_max"]) / 10

    # Штраф за УФ-индекс
    if uv is not None and uv > rules["uv_max"]:
        score -= 10 * (uv - rules["uv_max"])

    return max(0.0, round(score, 2))


# ==========================================
# 3. ПОИСК ОКОН (Правило 3 и 4 из README)
# ==========================================
def find_windows(
    times: List[str],
    temps: List[float],
    winds: List[float],
    precips: List[float],
    aqis: List[Optional[float]],
    uvs: List[Optional[float]],
    sport: str
) -> List[Dict[str, Any]]:
    """
    Ищет окна (часы подряд), где score >= 50.
    Возвращает список окон с деталями.
    """
    windows = []
    current_window = []

    for i in range(len(times)):
        # Берем данные на текущий час
        t = temps[i]
        w = winds[i]
        p = precips[i]
        # AQI и UV могут отсутствовать, если у нас деградация
        a = aqis[i] if aqis and i < len(aqis) else None
        u = uvs[i] if uvs and i < len(uvs) else None

        score = calculate_score(t, w, p, a, u, sport)

        # Если погода хорошая (score >= 50)
        if score >= 50:
            current_window.append({
                "time": times[i],
                "score": score,
                "details": {"temp": t, "wind": w, "precip": p, "aqi": a, "uv": u}
            })
        else:
            # Если погода испортилась, а окно было открыто — закрываем его
            if current_window:
                windows.append(current_window)
                current_window = []

    # Если последний час недели был хорошим — тоже закрываем окно
    if current_window:
        windows.append(current_window)

    # Формируем красивый вывод
    result = []
    for idx, win in enumerate(windows):
        start_time = win[0]["time"]
        end_time = win[-1]["time"]
        avg_score = sum(h["score"] for h in win) / len(win)
        
        # Нам нужно минимум 1-2 часа для тренировки (Правило 3)
        if len(win) >= 1:
            result.append({
                "window_index": idx,
                "start": start_time,
                "end": end_time,
                "duration_hours": len(win),
                "avg_score": round(avg_score, 2),
                "hourly_data": win
            })
            
    return result


# ==========================================
# 4. РАСПРЕДЕЛЕНИЕ ПО НЕДЕЛЕ (Правило 5 из README)
# ==========================================
def distribute_week(windows: List[Dict[str, Any]], sessions_per_week: int) -> List[Dict[str, Any]]:
    """
    Выбирает лучшие окна на неделю.
    (Упрощенная версия: просто берем топ-N по среднему score).
    """
    # Сортируем окна по убыванию среднего балла
    sorted_windows = sorted(windows, key=lambda x: x["avg_score"], reverse=True)
    
    # Берем нужное количество
    selected = sorted_windows[:sessions_per_week]
    
    # Возвращаем в хронологическом порядке (чтобы план выглядел логично)
    return sorted(selected, key=lambda x: x["start"])