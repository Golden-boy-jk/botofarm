import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- ДОБАВЛЯЕМ ПУТЬ К ПРИЛОЖЕНИЮ ---
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # папка botofarm/
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# --- ИМПОРТ НАСТРОЕК И БАЗЫ ---
from app.core.config import settings
from app.db.base import Base  # тут уже подтянутся все модели через импорт в base.py

# это объект конфигурации Alembic
config = context.config

# подсовываем Alembic наш URL из настроек
config.set_main_option("sqlalchemy.url", settings.database_url.unicode_string())

# Интерпретация конфигурационного файла для логгера.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata наших моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # полезно, чтобы ловить изменения типов полей
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
