from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.unit_school_associate import UnitSchoolAssociate
from app.domain.dtos.unit_school_associate.unit_school_associate_input import (
    UnitSchoolAssociateInput,
)
from app.service.crud.unit_school_associate_service import (
    UnitSchoolAssociateService,
)
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/unit_school_associates",
    tags=["Unit School Associate"]
)


@router.get("/", response_model=List[UnitSchoolAssociate])
def list_associations(
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 100
):
    return UnitSchoolAssociateService.get_all(
        session, start=start, limit=limit
    )


@router.get(
    "/by-key/{cod_unit}/{cod_school}/{cod_period}",
    response_model=UnitSchoolAssociate
)
def get_association(
    cod_unit: str,
    cod_school: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    assoc = UnitSchoolAssociateService.get_by_id(
        cod_unit, cod_school, cod_period, session
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
    return assoc


@router.get(
    "/by-unit/{cod_unit}/{cod_period}",
    response_model=List[UnitSchoolAssociate]
)
def get_schools_by_unit(
    cod_unit: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UnitSchoolAssociateService.get_by_unit(
        cod_unit, cod_period, session
    )


@router.get(
    "/by-school/{cod_school}/{cod_period}",
    response_model=List[UnitSchoolAssociate]
)
def get_units_by_school(
    cod_school: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UnitSchoolAssociateService.get_by_school(
        cod_school, cod_period, session
    )


@router.post(
    "/",
    response_model=UnitSchoolAssociate,
    status_code=status.HTTP_201_CREATED
)
def create_association(
    data: UnitSchoolAssociateInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UnitSchoolAssociateService.create(data, session)


@router.delete(
    "/{cod_unit}/{cod_school}/{cod_period}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_association(
    cod_unit: str,
    cod_school: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UnitSchoolAssociateService.delete(
        cod_unit, cod_school, cod_period, session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
