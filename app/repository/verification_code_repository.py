from sqlalchemy.orm import Session
from datetime import datetime
from app.domain.models.verification_code import VerificationCode


class VerificationCodeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, verification_code: VerificationCode):
        self.session.add(verification_code)
        self.session.commit()
        return verification_code

    def get_valid_code(self, email: str, code: str):
        return self.session.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.used == False,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()

    def mark_as_used(self, verification_code: VerificationCode):
        verification_code.used = True
        self.session.commit()

    def delete_expired(self, email: str):
        self.session.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        self.session.commit()
