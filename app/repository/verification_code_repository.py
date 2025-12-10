from sqlalchemy.orm import Session
from datetime import datetime
from app.domain.models.verification_code import VerificationCode
from app.utils.app_logger import AppLogger


logger = AppLogger(__file__, "verification_code_repository.log")


class VerificationCodeRepository:
    def __init__(self, session: Session):
        logger.info("VerificationCodeRepository initialized")
        self.session = session

    def create(self, verification_code: VerificationCode):
        logger.info(
            f"Creating verification code for email: {verification_code.email}"
        )
        self.session.add(verification_code)
        self.session.commit()
        return verification_code

    def get_valid_code(self, email: str, code: str):
        logger.info(f"Fetching valid code for email: {email}")
        logger.info(f"looking for code: {code}")
        logger.info(f"Current time: {datetime.utcnow()}")
        return self.session.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.used == False,  # noqa: E712
            VerificationCode.expires_at > datetime.utcnow()
        ).first()

    def mark_as_used(self, verification_code: VerificationCode):
        logger.info(
            f"Marking code as used for email: {verification_code.email}"
        )
        verification_code.used = True
        self.session.commit()

    def delete_expired(self, email: str):
        logger.info(f"Deleting expired codes for email: {email}")
        self.session.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        self.session.commit()
