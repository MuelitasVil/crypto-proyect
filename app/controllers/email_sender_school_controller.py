from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.email_sender_school import EmailSenderSchool
from app.domain.dtos.email_sender_school.email_sender_school_input import (
    EmailSenderSchoolInput
)

from app.service.crud.email_sender_school_service import (
    EmailSenderSchoolService,
)

from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/email_sender_schools",
    tags=["Email Sender School"]
)


@router.get("/", response_model=List[EmailSenderSchool])
def list_associations(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = 0,
    limit: int = 100
):
    return EmailSenderSchoolService.get_all(
        session, start=start, limit=limit
    )


@router.get("/{sender_id}/{cod_school}", response_model=EmailSenderSchool)
def get_association(
    sender_id: str,
    cod_school: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    assoc = EmailSenderSchoolService.get_by_id(sender_id, cod_school, session)
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
    return assoc


@router.post(
    "/",
    response_model=EmailSenderSchool,
    status_code=status.HTTP_201_CREATED
)
def create_association(
    data: EmailSenderSchoolInput,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    return EmailSenderSchoolService.create(data, session)


@router.delete(
    "/{sender_id}/{cod_school}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_association(
    sender_id: str,
    cod_school: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    deleted = EmailSenderSchoolService.delete(sender_id, cod_school, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
