from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

engine = create_engine(
    settings.database_url.unicode_string(),
    echo=settings.debug,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db():
    """Dependency для FastAPI: получить сессию БД и корректно её закрыть."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
