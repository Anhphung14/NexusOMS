from fastapi import APIRouter, Depends

from app.dependencies.auth import get_auth_service, get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=UserResponse)
def register(
        data: UserCreate,
        auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.register(data)

@router.post("/login")
def login(
        data: UserLogin,
        auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.login(data)