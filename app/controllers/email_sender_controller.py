from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.email_sender import EmailSender
from app.domain.dtos.email_sender.email_sender_input import EmailSenderInput
from app.service.crud.email_sender_service import EmailSenderService
from app.service.use_cases.fill_asociate_email_sender import (
    fill_associate_email_sender
)

router = APIRouter(prefix="/email_senders", tags=["Email Senders"])


@router.get("/", response_model=List[EmailSender])
def list_email_senders(
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 20
):
    return EmailSenderService.get_all(session, start=start, limit=limit)


@router.get("/{id}", response_model=EmailSender)
def get_email_sender(
    id: str,
    session: Session = Depends(get_session)
):
    sender = EmailSenderService.get_by_id(id, session)
    if not sender:
        raise HTTPException(status_code=404, detail="Email sender not found")
    return sender


@router.post(
    "/",
    response_model=EmailSender,
    status_code=status.HTTP_201_CREATED
)
def create_email_sender(
    data: EmailSenderInput,
    session: Session = Depends(get_session)
):
    return EmailSenderService.create(data, session)


@router.post(
    "/create-asociation-email-senders",
    status_code=status.HTTP_201_CREATED
)
def create_email_senders(
    session: Session = Depends(get_session),
    cod_period: str = ""
):
    return fill_associate_email_sender(session, cod_period)


@router.patch("/{id}", response_model=EmailSender)
def update_email_sender(
    id: str,
    data: EmailSenderInput,
    session: Session = Depends(get_session)
):
    updated = EmailSenderService.update(id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Email sender not found")
    return updated


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_sender(
    id: str,
    session: Session = Depends(get_session)
):
    deleted = EmailSenderService.delete(id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Email sender not found")
