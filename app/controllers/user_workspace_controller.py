from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.configuration.database import get_session
from app.service.crud.user_workspace_service import UserWorkspaceService
from app.domain.models.user_workspace import UserWorkspace
from app.domain.dtos.user_workspace.user_workspace_input import (
    UserWorkspaceInput,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/user-workspaces", tags=["User Workspaces"])


@router.get("/", response_model=List[UserWorkspace])
def list_user_workspaces(
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    start: int = 0,
    limit: int = 100
):
    return UserWorkspaceService.get_all(
        session, start=start, limit=limit
    )


@router.get("/{workspace_id}", response_model=UserWorkspace)
def get_user_workspace(
    workspace_id: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    workspace = UserWorkspaceService.get_by_id(workspace_id, session)
    if not workspace:
        raise HTTPException(status_code=404, detail="UserWorkspace not found")
    return workspace


@router.post(
    "/",
    response_model=UserWorkspace,
    status_code=status.HTTP_201_CREATED
)
def create_user_workspace(
    data: UserWorkspaceInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UserWorkspaceService.create(data, session)


@router.patch("/{workspace_id}", response_model=UserWorkspace)
def update_user_workspace(
    workspace_id: str, data: UserWorkspaceInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    updated = UserWorkspaceService.update(workspace_id, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="UserWorkspace not found")
    return updated


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_workspace(
    workspace_id: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UserWorkspaceService.delete(workspace_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="UserWorkspace not found")
