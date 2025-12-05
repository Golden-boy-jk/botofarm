# 🤖 Botofarm Service
![Botofarm CI](https://github.com/Golden-boy-jk/botofarm/actions/workflows/ci.yml/badge.svg)

REST-сервис для управления тестовыми пользователями ботофермы.\
Сервис предоставляет API для:

-   создания пользователей,
-   получения списка,
-   получения свободного пользователя,
-   блокировки и разблокировки,
-   health-check'ов,
-   авторизации по OAuth2 / JWT.

Проект полностью асинхронный (FastAPI + async SQLAlchemy + PostgreSQL).\
Готов к работе в Docker, совместим с Minikube/Kubernetes.\
Покрыт тестами (pytest + httpx).

## 📦 Стек технологий

-   FastAPI 0.115
-   Python 3.12
-   Pydantic v2
-   Async SQLAlchemy 2.0
-   PostgreSQL 14+
-   Alembic
-   Pytest + httpx + pytest-asyncio
-   Docker / docker-compose
-   OAuth2 (JWT)
-   Kubernetes манифесты (Minikube/KIND)

## 🚀 Запуск проекта

### Docker

    docker-compose up --build

Swagger: http://localhost:8000/docs

## 🧪 Тесты

    pytest -q

## ☸️ Kubernetes

Полный манифест находится в папке `k8s/`.

Пример запуска:

    minikube start --driver=docker
    minikube docker-env | Invoke-Expression
    docker build -t botofarm-web:latest .
    kubectl apply -f k8s/botofarm.yaml

## ✔ Что выполнено

  Требование                      Статус
  ------------------------------- --------
  Асинхронный сервис              ✔
  PostgreSQL + async SQLAlchemy   ✔
  Alembic миграции                ✔
  CRUD API                        ✔
  Health-checks                   ✔
  JWT авторизация                 ✔
  Dockerfile + docker-compose     ✔
  Pytest + coverage 75%+          ✔
  CI (GitHub Actions)             ✔
  Kubernetes манифесты            ✔

🗂 Структура проекта
```app/
  api/
    v1/
      users.py         # CRUD эндпоинты
      auth.py          # /token, get_current_user
      health.py        # liveness, readiness
  core/
    config.py          # настройки (env)
    security.py        # пароли + JWT
  db/
    base.py            # DeclarativeBase
    session.py         # async engine + session
  models/
    user.py            # модель User
  schemas/
    user.py            # Pydantic схемы
    token.py           # схема токена
  services/
    user_service.py    # бизнес-логика
  main.py              # FastAPI приложение
alembic/
  versions/
docker-compose.yml
Dockerfile
entrypoint.sh
k8s/botofarm.yaml      # Kubernetes манифесты
tests/                 # тесты
README.md
```

🏁 Лицензия

MIT.
Используйте, улучшайте, масштабируйте 😊
