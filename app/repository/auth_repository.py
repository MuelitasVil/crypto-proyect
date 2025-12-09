from sqlalchemy.orm import Session
from app.domain.models.system_user import SystemUser
from app.domain.models.jwt_token import Token


class AuthRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: SystemUser):
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_email(self, email: str):
        return self.session.get(SystemUser, email)

    def create_token(self, token: Token):
        self.session.add(token)
        self.session.commit()

    def token_exists(self, jwt_token: str) -> bool:
        return self.session.get(Token, jwt_token) is not None

    def delete_user(self, user_id: int):
        user = self.session.get(SystemUser, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
