import uuid
import jwt
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.domain.models.system_user import SystemUser
from app.domain.models.jwt_token import Token
from app.domain.models.verification_code import VerificationCode
from app.repository.auth_repository import AuthRepository
from app.repository.verification_code_repository import (
    VerificationCodeRepository
)
from app.service.ldap.ldap import LdapAdministrator
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "auth_service.log")

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CODE_EXPIRE_MINUTES = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# cn=admin,dc=dned,dc=unal,dc=edu,dc=co
# admin


class AuthService:
    @staticmethod
    def generate_code() -> str:
        logger.info("Generating verification code")
        return str(random.randint(100000, 999999))

    @staticmethod
    def register(email: str, password: str, session: Session) -> dict:
        logger.info(f"Registering user with email: {email}")
        auth_repo = AuthRepository(session)
        code_repo = VerificationCodeRepository(session)

        existing_user = auth_repo.get_user_by_email(email)

        if existing_user:
            logger.info(f"User with email {email} already exists")
            if existing_user.state:
                raise ValueError("User already exists")
            logger.info(f"Deleting expired codes for email: {email}")
            code_repo.delete_expired(email)
        else:
            logger.info(f"Creating new user with email: {email}")
            salt = uuid.uuid4().hex
            hashed = pwd_context.hash(password + salt)
            user = SystemUser(
                email=email,
                hashed_password=hashed,
                salt=salt,
                state=False
            )
            auth_repo.create_user(user)

        logger.info(f"Generating verification code for email: {email}")
        code = AuthService.generate_code()
        expires_at = (
            datetime.now(timezone.utc) + timedelta(minutes=CODE_EXPIRE_MINUTES)
        )
        verification = VerificationCode(
            email=email,
            code=code,
            expires_at=expires_at
        )
        code_repo.create(verification)

        logger.info(f"Verification code {code} created for email: {email}")

        return {"email": email, "message": "Verification code sent"}

    @staticmethod
    def verify_code(email: str, code: str, session: Session) -> bool:
        logger.info(f"Verifying code for email: {email}")
        auth_repo = AuthRepository(session)
        code_repo = VerificationCodeRepository(session)

        verification = code_repo.get_valid_code(email, code)
        if not verification:
            logger.info(f"Invalid or expired code for email: {email}")
            return False

        code_repo.mark_as_used(verification)

        user = auth_repo.get_user_by_email(email)
        logger.info(f"Activating user account for email: {email}")
        if user:
            logger.info(f"User found for email: {email}, activating account")
            user.state = True
            session.commit()
            return True

        return False

    @staticmethod
    def login(
        email: str, password: str, session: Session, use_ldap=True
    ) -> str:
        logger.info(f"Attempting login for email: {email}")
        if use_ldap:
            logger.info(f"Using LDAP for authentication of email: {email}")
            ldap_admin = LdapAdministrator()
            ldap_response = ldap_admin.check_user_credentials(email, password)
            if not ldap_response['respuesta']:
                return None

        logger.info(f"Using database for authentication of email: {email}")
        repo = AuthRepository(session)
        user = repo.get_user_by_email(email)
        if not user or not user.state:
            return None

        logger.info(f"Verifying password for email: {email}")
        if not pwd_context.verify(password + user.salt, user.hashed_password):
            return None

        logger.info(f"Generating JWT token for email: {email}")
        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        payload = {"sub": user.email, "exp": expire}
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        logger.info(f"Storing JWT token for email: {email}")
        repo.create_token(
            Token(
                jwt_token=jwt_token,
                email=user.email,
                created_at=datetime.utcnow()
            )
        )
        return jwt_token
