from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.user_unit_associate import UserUnitAssociate
from app.domain.dtos.user_unit_associate.user_unit_associate_input import (
    UserUnitAssociateInput
)
from app.service.crud.user_unit_associate_service import (
    UserUnitAssociateService,
)
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/user_unit_associates",
    tags=["User Unit Associate"]
)


@router.get("/", response_model=List[UserUnitAssociate])
def list_associations(
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 100
):
    return UserUnitAssociateService.get_all(session, start=start, limit=limit)


@router.get(
    "/by-key/{email_unal}/{cod_unit}/{cod_period}",
    response_model=UserUnitAssociate
)
def get_association(
    email_unal: str,
    cod_unit: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    assoc = UserUnitAssociateService.get_by_id(
        email_unal, cod_unit, cod_period, session
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
    return assoc


@router.get(
    "/by-user/{email_unal}/{cod_period}",
    response_model=List[UserUnitAssociate]
)
def get_units_by_user(
    email_unal: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UserUnitAssociateService.get_by_user(
        email_unal, cod_period, session
    )


@router.get(
    "/by-unit/{cod_unit}/{cod_period}",

    response_model=List[UserUnitAssociate]
)
def get_users_by_unit(
    cod_unit: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UserUnitAssociateService.get_by_unit(
        cod_unit, cod_period, session
    )


@router.post(
    "/",
    response_model=UserUnitAssociate,
    status_code=status.HTTP_201_CREATED
)
def create_association(
    data: UserUnitAssociateInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UserUnitAssociateService.create(data, session)


@router.delete(
    "/{email_unal}/{cod_unit}/{cod_period}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_association(
    email_unal: str,
    cod_unit: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UserUnitAssociateService.delete(
        email_unal, cod_unit, cod_period, session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
