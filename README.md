# botofarm
# 🤖 Botofarm Service

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
-   Pytest
-   Docker / docker-compose
-   OAuth2 (JWT)
-   Kubernetes (манифесты)

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
