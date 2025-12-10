from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.school_headquarters_associate import (
    SchoolHeadquartersAssociate
)
from app.domain.dtos.school_headquarters_associate.school_headquarters_associate_input import (  # noqa: E501 ignora error flake8
    SchoolHeadquartersAssociateInput
)
from app.service.crud.school_headquarters_associate_service import (
    SchoolHeadquartersAssociateService
)
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/school_headquarters_associates",
    tags=["School Headquarters Associate"]
)


@router.get("/", response_model=List[SchoolHeadquartersAssociate])
def list_associations(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = 0,
    limit: int = 100
):
    return SchoolHeadquartersAssociateService.get_all(
        session, start=start, limit=limit
    )


@router.get("/by-key/{cod_school}/{cod_headquarters}/{cod_period}",
            response_model=SchoolHeadquartersAssociate)
def get_association(
    cod_school: str,
    cod_headquarters: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    assoc = SchoolHeadquartersAssociateService.get_by_id(
        cod_school,
        cod_headquarters,
        cod_period,
        session
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="Association not found")
    return assoc


@router.get(
        "/by-school/{cod_school}/{cod_period}",
        response_model=List[SchoolHeadquartersAssociate]
)
def get_headerquarters_by_school(
    cod_school: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return SchoolHeadquartersAssociateService.get_by_school(
        cod_school,
        cod_period,
        session
    )


@router.get(
        "/by-headquarters/{cod_headquarters}/{cod_period}",
        response_model=List[SchoolHeadquartersAssociate]
)
def get_schools_by_headquarters(
    cod_headquarters: str,
    cod_period: str = None,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return SchoolHeadquartersAssociateService.get_by_headquarters(
        cod_headquarters,
        cod_period,
        session
    )


@router.post(
    "/",
    response_model=SchoolHeadquartersAssociate,
    status_code=status.HTTP_201_CREATED
)
def create_association(
    data: SchoolHeadquartersAssociateInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return SchoolHeadquartersAssociateService.create(data, session)


@router.delete(
    "/{cod_school}/{cod_headquarters}/{cod_period}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_association(
    cod_school: str,
    cod_headquarters: str,
    cod_period: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = SchoolHeadquartersAssociateService.delete(
        cod_school,
        cod_headquarters,
        cod_period,
        session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
