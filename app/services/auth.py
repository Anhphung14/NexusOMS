from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
)
from app.schemas.auth import TokenResponse


class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, data: UserCreate) -> UserResponse:
        existing_user = self.user_repository.get_by_email(data.email)

        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = hash_password(data.password)

        user = User(
            email=data.email,
            hashed_password=hashed_password,
            full_name=None,
        )

        user = self.user_repository.create(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
        )

    def login(self, data: UserLogin) -> TokenResponse:
        user = self.user_repository.get_by_email(data.email)

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User is not active")

        token = create_access_token(user_id=user.id)

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )