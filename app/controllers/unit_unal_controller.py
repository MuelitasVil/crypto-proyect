from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.unit_unal import UnitUnal
from app.domain.dtos.unit_unal.unit_unal_input import UnitUnalInput
from app.service.crud.unit_unal_service import UnitUnalService
from app.service.use_cases.get_list_email_organization import (
    get_email_list_of_unit
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/units_unal", tags=["Units UNAL"])


@router.get("/", response_model=List[UnitUnal])
def list_units(
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 100
):
    return UnitUnalService.get_all(
        session, start=start, limit=limit
    )


@router.get("/{cod_unit}", response_model=UnitUnal)
def get_unit(
    cod_unit: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    unit = UnitUnalService.get_by_id(
        cod_unit,
        session
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


@router.get("/get-email-list/{cod_unit}/{cod_period}")
def define_get_unit(
    cod_unit: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    unit = UnitUnalService.get_by_id(
        cod_unit,
        session
    )
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    emails = get_email_list_of_unit(session, cod_unit, cod_period)
    if not emails:
        raise HTTPException(
            status_code=404,
            detail="No emails found for this unit and period"
        )

    return emails


@router.post("/", response_model=UnitUnal, status_code=status.HTTP_201_CREATED)
def create_unit(
    data: UnitUnalInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UnitUnalService.create(data, session)


@router.patch("/{cod_unit}", response_model=UnitUnal)
def update_unit(
    cod_unit: str,
    data: UnitUnalInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    updated = UnitUnalService.update(cod_unit, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Unit not found")
    return updated


@router.delete("/{cod_unit}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    cod_unit: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UnitUnalService.delete(cod_unit, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Unit not found")
