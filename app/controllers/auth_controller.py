from app.domain.dtos.auth.register_input import RegisterInput
from app.domain.dtos.auth.login_input import LoginInput
from app.domain.dtos.auth.verify_code_input import VerifyCodeInput
from app.service.crud.auth_service import AuthService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.configuration.database import get_session
from app.utils.rate_limiter import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(data: RegisterInput, session: Session = Depends(get_session)):
    try:
        result = AuthService.register(data.email, data.password, session)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
def verify(data: VerifyCodeInput, session: Session = Depends(get_session)):
    success = AuthService.verify_code(data.email, data.code, session)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    return {"message": "Email verified successfully"}


@router.post("/login")
def login(
    data: LoginInput,
    session: Session = Depends(get_session),
    _: None = Depends(rate_limit(max_requests=5, window_seconds=60))
):
    token = AuthService.login(data.email, data.password, session)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}