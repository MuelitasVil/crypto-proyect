from sqlalchemy.orm import Session
from typing import List, Optional

from app.repository.email_sender_school_repository import (
    EmailSenderSchoolRepository
)

from app.domain.models.email_sender_school import EmailSenderSchool

from app.domain.dtos.email_sender_school.email_sender_school_input import (
    EmailSenderSchoolInput
)


class EmailSenderSchoolService:
    @staticmethod
    def get_all(
        session: Session, start: int = 0, limit: int = 100
    ) -> List[EmailSenderSchool]:
        repo = EmailSenderSchoolRepository(session)
        return repo.get_all(start=start, limit=limit)

    @staticmethod
    def get_by_id(
        sender_id: str,
        cod_school: str,
        session: Session
    ) -> Optional[
        EmailSenderSchool
    ]:
        return EmailSenderSchoolRepository(session).get_by_id(
            sender_id, cod_school
        )

    @staticmethod
    def create(
        input_data: EmailSenderSchoolInput,
        session: Session
    ) -> EmailSenderSchool:
        assoc = EmailSenderSchool(**input_data.model_dump())
        return EmailSenderSchoolRepository(session).create(assoc)

    @staticmethod
    def delete(sender_id: str, cod_school: str, session: Session) -> bool:
        return EmailSenderSchoolRepository(session).delete(
            sender_id, cod_school
        )

    # TODO: this methond break the pattern, fix it later
    # the input is not a dto, its a model.
    @staticmethod
    def bulk_insert_ignore(
        email_schools: List[EmailSenderSchool],
        session: Session
    ):
        """
        Inserta en bulk usuarios.
        Si hay duplicados en email_unal, MySQL los ignora.
        """
        user_models = [
            EmailSenderSchool(**u.model_dump(exclude_unset=True))
            for u in email_schools
        ]
        repo = EmailSenderSchoolRepository(session)
        repo.bulk_insert_ignore(user_models)
        return {
            "inserted": len(email_schools),
            "duplicates_ignored": True,
        }
