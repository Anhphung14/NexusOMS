from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    def __init__(self):
        self.user_repository = User

    def update_user(
            self,
            current_user: User,
            data: UserUpdate
    ) -> UserResponse:
        if data.email is not None:
            existing_user = self.user_repository.get_by_email(data.email)

            if existing_user and existing_user.id != current_user.id:
                raise ValueError("Email already registered")

            current_user.email = data.email

        if data.full_name is not None:
            current_user.full_name = data.full_name

        user = self.user_repository.update(current_user)

        return UserResponse(
            id = user.id,
            email = user.email,
            full_name = user.full_name
        )






