from datetime import datetime
from pydantic import EmailStr, Field, model_validator
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(min_length = 8, max_length = 128)
    confirm_password: str = Field(min_length = 8, max_length = 128)

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")

        return self

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class UserUpdate(SQLModel):
    email: EmailStr | None = None
    full_name: str | None = None

class UserResponse(SQLModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    created_at: datetime

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = 'bearer'
