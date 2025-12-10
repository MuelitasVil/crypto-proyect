from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.school import School
from app.domain.dtos.school.school_input import SchoolInput
from app.service.crud.school_service import SchoolService

from app.service.use_cases.get_list_email_organization import (
    get_email_list_of_school
)

from app.utils.auth import get_current_user

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.get("/", response_model=List[School])
def list_schools(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = 0,
    limit: int = 100
):
    return SchoolService.get_all(session, start=start, limit=limit)


@router.get("/{cod_school}", response_model=School)
def get_school(
    cod_school: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    school = SchoolService.get_by_id(cod_school, session)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.get("/get-email-list/{cod_school}/{cod_period}")
def define_get_school(
    cod_school: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    school = SchoolService.get_by_id(
        cod_school,
        session
    )
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    emails = get_email_list_of_school(session, cod_school, cod_period)
    if not emails:
        raise HTTPException(
            status_code=404,
            detail="No emails found for this school and period"
        )

    return emails


@router.post("/", response_model=School, status_code=status.HTTP_201_CREATED)
def create_school(
    data: SchoolInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return SchoolService.create(data, session)


@router.patch("/{cod_school}", response_model=School)
def update_school(
    cod_school: str,
    data: SchoolInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    updated = SchoolService.update(cod_school, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="School not found")
    return updated


@router.delete("/{cod_school}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    cod_school: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = SchoolService.delete(cod_school, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="School not found")
