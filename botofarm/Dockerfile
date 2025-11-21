# -------------------------------
#  Production-ready Dockerfile
# -------------------------------

FROM python:3.12-slim

# Общие переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt отдельно (правильно для кэширования Docker)
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение и alembic
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# Копируем entrypoint
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Порт внутри контейнера
EXPOSE 8000

# -------------------------------
# HEALTHCHECK — продовый
# -------------------------------
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# -------------------------------
# Запуск через entrypoint.sh
# -------------------------------
ENTRYPOINT ["./entrypoint.sh"]

