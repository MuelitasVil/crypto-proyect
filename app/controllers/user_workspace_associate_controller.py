from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.user_workspace_associate import UserWorkspaceAssociate
from app.domain.dtos.user_workspace_associate.user_workspace_associate_input import (  # noqa: E501 ignora error flake8
    UserWorkspaceAssociateInput
)
from app.service.crud.user_workspace_associate_service import (
    UserWorkspaceAssociateService
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/associates", tags=["UserWorkspaceAssociate"])


@router.post(
    "/",
    response_model=UserWorkspaceAssociate,
    status_code=status.HTTP_201_CREATED
)
def create_associate(
    data: UserWorkspaceAssociateInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return UserWorkspaceAssociateService.create(data, session)


@router.get("/", response_model=List[UserWorkspaceAssociate])
def list_associates(
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 100
):
    return UserWorkspaceAssociateService.get_all(
        session, start=start, limit=limit
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_associate(
    data: UserWorkspaceAssociateInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UserWorkspaceAssociateService.delete(
        data.email_unal,
        data.user_workspace_id,
        data.cod_period,
        session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
