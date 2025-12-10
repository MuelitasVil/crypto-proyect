from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from typing import List

from app.configuration.database import get_session
from app.domain.models.user_unal import UserUnal
from app.domain.dtos.user_unal.user_unal_input import UserUnalInput
from app.service.crud.user_unal_service import UserUnalService
from app.domain.dtos.user_unal.user_info import UserInfoAssociation
from app.service.use_cases.get_info_user import get_info_user
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users_unal", tags=["Users UNAL"])


@router.get("/", response_model=List[UserUnal])
def list_users(
    session: Session = Depends(get_session),
    user_email: str = Depends(get_current_user),
    start: int = Query(0, ge=0),
    limit: int = Query(20, ge=1)
):
    return UserUnalService.get_all(session, start=start, limit=limit)


@router.get("/{email_unal}", response_model=UserUnal)
def get_user(
    email_unal: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user = UserUnalService.get_by_email(email_unal, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/user_info/{email_unal}", response_model=UserInfoAssociation)
def get_user_info(
    email_unal: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_info = get_info_user(email_unal, session)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info


@router.post("/", response_model=UserUnal, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserUnalInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return UserUnalService.create(data, session)


@router.patch("/{email_unal}", response_model=UserUnal)
def update_user(
    email_unal: str,
    data: UserUnalInput,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    updated = UserUnalService.update(email_unal, data, session)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/{email_unal}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    email_unal: str,
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deleted = UserUnalService.delete(email_unal, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
