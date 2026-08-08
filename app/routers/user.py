from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.models.user import User
from app.services import user

router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
        current_user: User = Depends(get_current_user)
):
    return current_user

@router.patch(
    "/update",
    response_model=UserResponse
)
def update(
        data: UserUpdate,
        current_user: User = Depends(get_current_user),
        user_service: user.UserService = Depends(get_current_user)
):
    return user_service.update(
        current_user,
        data
    )