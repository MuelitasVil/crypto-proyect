from sqlmodel import Session, insert, select
from typing import List, Optional

from app.domain.models.type_user_association import TypeUserAssociation


class TypeUserAssociationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(
            self, start: int = 0, limit: int = 100
    ) -> List[TypeUserAssociation]:
        return self.session.exec(
            select(TypeUserAssociation).offset(start).limit(limit)
        ).all()

    def get_by_id(
            self,
            email_unal: str,
            type_user_id: str,
            cod_period: str
    ) -> Optional[TypeUserAssociation]:
        return self.session.get(
            TypeUserAssociation,
            (email_unal, type_user_id, cod_period)
        )

    def create(self, assoc: TypeUserAssociation) -> TypeUserAssociation:
        self.session.add(assoc)
        self.session.commit()
        self.session.refresh(assoc)
        return assoc

    def delete(
            self,
            email_unal: str,
            type_user_id: str,
            cod_period: str
    ) -> bool:
        assoc = self.get_by_id(email_unal, type_user_id, cod_period)
        if assoc:
            self.session.delete(assoc)
            self.session.commit()
            return True
        return False

    def bulk_insert_ignore(
        self, unitUnal: List[TypeUserAssociation]
    ):
        """
        Inserta múltiples usuarios en la tabla.
        Si encuentra PK duplicada (email_unal), ignora ese registro.
        """
        stmt = insert(TypeUserAssociation).values(
            [u.model_dump() for u in unitUnal]
        )
        stmt = stmt.prefix_with("IGNORE")
        self.session.exec(stmt)
        self.session.commit()
