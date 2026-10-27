# Базовый образ — Python 3.12 на минимальном Linux (slim)
FROM python:3.12-slim

# Отключаем создание .pyc-файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем только requirements.txt
# Это ускоряет пересборку: если код изменится, библиотеки не переустанавливаются
COPY requirements.txt .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь остальной код
COPY . .

# Открываем порт (документация, реально порт публикует docker-compose)
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
