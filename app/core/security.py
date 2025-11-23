from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto",
# )
""" версия bcrypt не очень дружит с passlib, как оказалось :)))  """

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Получить хэш пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль на соответствие хэшу."""
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------
# JWT-настройки и утилиты
# -----------------------------

# В реальном проде это нужно брать из окружения
SECRET_KEY = "super-secret-key-change-me"  # можешь вынести в .env/Settings, если захочешь
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Создать JWT-токен.
    subject — обычно id пользователя (строкой) или его логин.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire}

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Декодировать JWT-токен и вернуть payload.

    Если токен невалиден/протух — кидаем JWTError, а обработаем уже в зависимостях.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload