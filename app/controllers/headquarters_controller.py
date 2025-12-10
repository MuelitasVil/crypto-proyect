from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.headquarters import Headquarters
from app.domain.dtos.headquarters.headquarters_input import HeadquartersInput
from app.service.crud.headquarters_service import HeadquartersService

from app.service.use_cases.get_list_email_organization import (
    get_email_list_of_headquarters
)

from app.utils.auth import get_current_user

router = APIRouter(prefix="/headquarters", tags=["Headquarters"])


@router.get("/", response_model=List[Headquarters])
def list_headquarters(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = 0,
    limit: int = 100
):
    return HeadquartersService.get_all(session, start=start, limit=limit)


@router.get("/by_code/{cod_headquarters}", response_model=Headquarters)
def get_headquarters(
    cod_headquarters: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    hq = HeadquartersService.get_by_id(cod_headquarters, session)
    if not hq:
        raise HTTPException(status_code=404, detail="Headquarters not found")
    return hq


@router.get("/by_name/{name_headquarters}", response_model=List[Headquarters])
def get_headquarters_by_name(
    name_headquarters: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
):
    hq = HeadquartersService.get_by_name(name_headquarters, session)
    if not hq:
        raise HTTPException(status_code=404, detail="Headquarters not found")
    return hq


@router.get("/get-email-list/{cod_headquarters}/{cod_period}")
def define_get_headquarters(
    cod_headquarters: str,
    cod_period: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    hq = HeadquartersService.get_by_id(
        cod_headquarters,
        session
    )
    if not hq:
        raise HTTPException(status_code=404, detail="Headquarters not found")

    emails = get_email_list_of_headquarters(
        session,
        cod_headquarters,
        cod_period
    )
    if not emails:
        raise HTTPException(
            status_code=404,
            detail="No emails found for this headquarters and period"
        )

    return emails


@router.post(
    "/",
    response_model=Headquarters,
    status_code=status.HTTP_201_CREATED
)
def create_headquarters(
    data: HeadquartersInput,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    return HeadquartersService.create(data, session)


@router.patch("/{cod_headquarters}", response_model=Headquarters)
def update_headquarters(
    cod_headquarters: str,
    data: HeadquartersInput,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    updated = HeadquartersService.update(cod_headquarters, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Headquarters not found")
    return updated


@router.delete("/{cod_headquarters}", status_code=status.HTTP_204_NO_CONTENT)
def delete_headquarters(
    cod_headquarters: str,
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user)
):
    deleted = HeadquartersService.delete(cod_headquarters, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Headquarters not found")
