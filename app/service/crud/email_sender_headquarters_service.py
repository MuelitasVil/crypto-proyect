from sqlalchemy.orm import Session
from typing import List, Optional

from app.repository.email_sender_headquarters_repository import (
    EmailSenderHeadquartersRepository
)
from app.domain.models.email_sender_headquarters import EmailSenderHeadquarters
from app.domain.dtos.email_sender_headquarters.email_sender_headquarters_input import (  # noqa: E501 ignora error flake8
    EmailSenderHeadquartersInput
)


class EmailSenderHeadquartersService:
    @staticmethod
    def get_all(
        session: Session, start: int = 0, limit: int = 100
    ) -> List[EmailSenderHeadquarters]:
        repo = EmailSenderHeadquartersRepository(session)
        return repo.get_all(start=start, limit=limit)

    @staticmethod
    def get_by_id(
        sender_id: str,
        cod_headquarters: str,
        session: Session
    ) -> Optional[EmailSenderHeadquarters]:
        return EmailSenderHeadquartersRepository(session).get_by_id(
            sender_id, cod_headquarters
        )

    @staticmethod
    def create(
        input_data: EmailSenderHeadquartersInput,
        session: Session
    ) -> EmailSenderHeadquarters:
        assoc = EmailSenderHeadquarters(**input_data.model_dump())
        return EmailSenderHeadquartersRepository(session).create(assoc)

    @staticmethod
    def delete(
        sender_id: str,
        cod_headquarters: str,
        session: Session
    ) -> bool:
        return EmailSenderHeadquartersRepository(session).delete(
            sender_id, cod_headquarters
        )

    # TODO: this methond break the pattern, fix it later
    # the input is not a dto, its a model.
    @staticmethod
    def bulk_insert_ignore(
        email_headquarters: List[EmailSenderHeadquarters],
        session: Session
    ):
        """
        Inserta en bulk usuarios.
        Si hay duplicados en email_unal, MySQL los ignora.
        """
        user_models = [
            EmailSenderHeadquarters(**u.model_dump(exclude_unset=True))
            for u in email_headquarters
        ]
        repo = EmailSenderHeadquartersRepository(session)
        repo.bulk_insert_ignore(user_models)
        return {
            "inserted": len(email_headquarters),
            "duplicates_ignored": True,
        }
