from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    debug: bool = True
    lock_timeout_seconds: int = 300 # 5 минут lock

    @property
    def async_database_url(self) -> str:
        """
        Генерирует async-URL (postgresql+asyncpg://....)
        """
        url = self.database_url.unicode_string()
        return url.replace("postgresql+psycopg2", "postgresql+asyncpg")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

