from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    app_name: str = "Botfarm Service"
    debug: bool = True

    database_url: PostgresDsn

    # на будущее: сюда же можно добавить настройки auth, jwt и т.д.

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
