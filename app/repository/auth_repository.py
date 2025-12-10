from sqlalchemy.orm import Session
from app.domain.models.system_user import SystemUser
from app.domain.models.jwt_token import Token
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "auth_repository.log")


class AuthRepository:
    def __init__(self, session: Session):
        logger.info("AuthRepository initialized")
        self.session = session

    def create_user(self, user: SystemUser):
        logger.info(f"Creating user with email: {user.email}")
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_email(self, email: str):
        logger.info(f"Fetching user with email: {email}")
        return self.session.get(SystemUser, email)

    def create_token(self, token: Token):
        logger.info(f"Creating token for user_id: {token.email}")
        self.session.add(token)
        self.session.commit()

    def token_exists(self, jwt_token: str) -> bool:
        logger.info(f"Checking existence of token: {jwt_token}")
        return self.session.get(Token, jwt_token) is not None

    def delete_user(self, user_id: int):
        logger.info(f"Deleting user with id: {user_id}")
        user = self.session.get(SystemUser, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
