from sqlmodel import Session, insert, select
from typing import List, Optional

from app.domain.models.email_sender_unit import EmailSenderUnit


class EmailSenderUnitRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(
        self, start: int = 0, limit: int = 100
    ) -> List[EmailSenderUnit]:
        return self.session.exec(
            select(EmailSenderUnit).offset(start).limit(limit)
        ).all()

    def get_by_id(
        self,
        sender_id: str,
        cod_unit: str
    ) -> Optional[EmailSenderUnit]:
        return self.session.get(EmailSenderUnit, (sender_id, cod_unit))

    def create(self, assoc: EmailSenderUnit) -> EmailSenderUnit:
        self.session.add(assoc)
        self.session.commit()
        self.session.refresh(assoc)
        return assoc

    def delete(self, sender_id: str, cod_unit: str) -> bool:
        assoc = self.get_by_id(sender_id, cod_unit)
        if assoc:
            self.session.delete(assoc)
            self.session.commit()
            return True
        return False

    def bulk_insert_ignore(
        self, unit_emails: List[EmailSenderUnit]
    ):
        """
        Inserta múltiples usuarios en la tabla.
        Si encuentra PK duplicada (email_unal), ignora ese registro.
        """
        stmt = insert(EmailSenderUnit).values(
            [u.model_dump() for u in unit_emails]
        )
        stmt = stmt.prefix_with("IGNORE")
        self.session.exec(stmt)
        self.session.commit()
