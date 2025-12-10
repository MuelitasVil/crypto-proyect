import uuid
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.domain.models.system_user import SystemUser
from app.domain.models.jwt_token import Token
from app.repository.auth_repository import AuthRepository
from app.service.ldap.ldap import ldapAdministrator

SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# cn=admin,dc=dned,dc=unal,dc=edu,dc=co
# admin

class AuthService:
    @staticmethod
    def register(email: str, password: str, session: Session) -> SystemUser:
        repo = AuthRepository(session)
        salt = uuid.uuid4().hex
        hashed = pwd_context.hash(password + salt)
        user = SystemUser(
            email=email,
            hashed_password=hashed,
            salt=salt
        )
        created_user = repo.create_user(user)

        ldap_admin = ldapAdministrator()
        ldap_user = user(
            username=email,
            password=password,
            name="Nombre",
            lastname="Apellido",
            email=email
        )

        ldap_response = ldap_admin.create_user(ldap_user)
        if not ldap_response['respuesta']:
            repo.delete_user(created_user.id)
            return None

        return created_user

    @staticmethod
    def login(
        email: str, password: str, session: Session, use_ldap=True
    ) -> str:
        if use_ldap:
            ldap_admin = ldapAdministrator()
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
