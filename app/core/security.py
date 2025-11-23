from passlib.context import CryptContext

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
