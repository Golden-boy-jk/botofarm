from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.token import Token
from app.services.user_service import authenticate_user, get_user_by_id
from app.core.security import create_access_token, decode_access_token

router = APIRouter(tags=["auth"])

# tokenUrl — как его будет дергать клиент.
# Так как в main.py стоит prefix="/api/v1", в итоге это будет /api/v1/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


@router.post("/token", response_model=Token, summary="Получить JWT-токен по логину и паролю")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Стандартный OAuth2 Password Flow:
    - принимает username + password
    - проверяет пользователя
    - возвращает access_token
    """
    # В нашем случае username = email (login)
    user = await authenticate_user(db, login=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # В subject кладём id пользователя (строкой)
    access_token = create_access_token(subject=str(user.id))

    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Зависимость для получения текущего пользователя по JWT-токену.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except Exception:
        # JWTError и другие — всё сюда
        raise credentials_exception

    try:
        user_id = UUID(sub)
    except ValueError:
        raise credentials_exception

    user = await get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception

    return user
