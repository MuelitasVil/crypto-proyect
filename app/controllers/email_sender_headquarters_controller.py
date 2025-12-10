from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.email_sender_headquarters import EmailSenderHeadquarters
from app.domain.dtos.email_sender_headquarters.email_sender_headquarters_input import (  # noqa: E501 ignora error flake8
    EmailSenderHeadquartersInput
)
from app.service.crud.email_sender_headquarters_service import (
    EmailSenderHeadquartersService
)

from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/email_sender_headquarters",
    tags=["Email Sender Headquarters"]
)


@router.get("/", response_model=List[EmailSenderHeadquarters])
def list_associations(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = 0,
    limit: int = 100
):
    return EmailSenderHeadquartersService.get_all(
        session, start=start, limit=limit
    )


@router.get(
    "/{sender_id}/{cod_headquarters}",
    response_model=EmailSenderHeadquarters
)
def get_association(
    sender_id: str,
    cod_headquarters: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    assoc = EmailSenderHeadquartersService.get_by_id(
        sender_id, cod_headquarters, session
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
    return assoc


@router.post(
    "/",
    response_model=EmailSenderHeadquarters,
    status_code=status.HTTP_201_CREATED
)
def create_association(
    data: EmailSenderHeadquartersInput,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    return EmailSenderHeadquartersService.create(data, session)


@router.delete(
    "/{sender_id}/{cod_headquarters}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_association(
    sender_id: str,
    cod_headquarters: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    deleted = EmailSenderHeadquartersService.delete(
        sender_id, cod_headquarters, session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
