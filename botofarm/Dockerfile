# Dockerfile
# Базовый образ Python (можешь потом поменять на 3.12)
FROM python:3.12-slim

# Не интерактивный режим внутри контейнера
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем системные зависимости (для psycopg2 и т.п.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем список зависимостей
COPY requirements.txt .

# Копируем приложение и alembic
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# Копируем entrypoint-скрипт
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app ./app

# Если есть файл .env, тоже можно скопировать (или использовать env_file в docker-compose)
# COPY .env ./.env

# Открываем порт для uvicorn
EXPOSE 8000

# Запуск сервиса
CMD ["./entrypoint.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
