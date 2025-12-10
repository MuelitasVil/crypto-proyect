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
from app.repository.verification_code_repository import VerificationCodeRepository

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CODE_EXPIRE_MINUTES = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def generate_code() -> str:
        return str(random.randint(100000, 999999))

    @staticmethod
    def register(email: str, password: str, session: Session) -> dict:
        auth_repo = AuthRepository(session)
        code_repo = VerificationCodeRepository(session)

        existing_user = auth_repo.get_user_by_email(email)

        if existing_user:
            if existing_user.state:
                raise ValueError("User already exists")
            code_repo.delete_expired(email)
        else:
            salt = uuid.uuid4().hex
            hashed = pwd_context.hash(password + salt)
            user = SystemUser(
                email=email,
                hashed_password=hashed,
                salt=salt,
                state=False
            )
            auth_repo.create_user(user)

        code = AuthService.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)

        verification = VerificationCode(
            email=email,
            code=code,
            expires_at=expires_at
        )
        code_repo.create(verification)

        print(f"Verification code for {email}: {code}")

        return {"email": email, "message": "Verification code sent"}

    @staticmethod
    def verify_code(email: str, code: str, session: Session) -> bool:
        auth_repo = AuthRepository(session)
        code_repo = VerificationCodeRepository(session)

        verification = code_repo.get_valid_code(email, code)
        if not verification:
            return False

        code_repo.mark_as_used(verification)

        user = auth_repo.get_user_by_email(email)
        if user:
            user.state = True
            session.commit()
            return True

        return False

    @staticmethod
    def login(email: str, password: str, session: Session) -> str:
        repo = AuthRepository(session)
        user = repo.get_user_by_email(email)
        if not user or not user.state:
            return None

        if not pwd_context.verify(password + user.salt, user.hashed_password):
            return None

        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        payload = {"sub": user.email, "exp": expire}
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        repo.create_token(
            Token(
                jwt_token=jwt_token,
                email=user.email,
                created_at=datetime.utcnow()
            )
        )
        return jwt_token
