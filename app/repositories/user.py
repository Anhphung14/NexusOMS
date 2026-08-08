from sqlmodel import Session, select
from app.models.user import User

class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        return self.session.exec(statement).first()

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)

        return self.session.exec(statement).first()

    def update_user(self, user: User) -> User | None:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user