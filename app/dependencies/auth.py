import token

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session
from starlette import status

from app.core.security import decode_access_token
from app.db.database import get_session
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)

def get_user_repository(
        session: Session = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = user_repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user

def get_user_repository(
        session: Session = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)

def get_auth_service(
        user_repository: UserRepository = Depends(get_user_repository)
)->AuthService:
    return AuthService(user_repository)

def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)