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
<<<<<<< HEAD
from app.service.ldap.ldap import LdapAdministrator, User
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "auth_service.log")
=======
from app.repository.verification_code_repository import VerificationCodeRepository
>>>>>>> origin/dev

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CODE_EXPIRE_MINUTES = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# cn=admin,dc=dned,dc=unal,dc=edu,dc=co
# admin


class AuthService:
    @staticmethod
<<<<<<< HEAD
    def register(email: str, password: str, session: Session) -> SystemUser:
        logger.info(f"Starting registration for email: {email}")
        repo = AuthRepository(session)
        salt = uuid.uuid4().hex
        hashed = pwd_context.hash(password + salt)
        user = SystemUser(
=======
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
>>>>>>> origin/dev
            email=email,
            code=code,
            expires_at=expires_at
        )
<<<<<<< HEAD
        created_user = repo.create_user(user)
        logger.info(f"User created in database with email: {email}")

        ldap_admin = LdapAdministrator()
        ldap_user = User(
            username=email,
            password=password,
            name="Nombre",
            lastname="Apellido",
            email=email
        )

        ldap_response = ldap_admin.create_user(ldap_user)
        logger.info(
            f"LDAP user creation response for email {email}: {ldap_response}"
        )
        if not ldap_response['respuesta']:
            logger.error(
                f"LDAP user creation failed for email {email}"
                f", rolling back database entry."
            )
            repo.delete_user(created_user.email)
            return None

        return user
=======
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
>>>>>>> origin/dev

    @staticmethod
    def login(
        email: str, password: str, session: Session, use_ldap=True
    ) -> str:
        if use_ldap:
            ldap_admin = LdapAdministrator()
            ldap_response = ldap_admin.check_user_credentials(email, password)
            if not ldap_response['respuesta']:
                return None

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
