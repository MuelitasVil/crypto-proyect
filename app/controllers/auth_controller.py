from app.domain.dtos.auth.register_input import RegisterInput
from app.domain.dtos.auth.login_input import LoginInput
from app.service.crud.auth_service import AuthService
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.configuration.database import get_session
from app.utils.rate_limiter import rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(data: RegisterInput, session: Session = Depends(get_session)):
    user = AuthService.register(data.email, data.password, session)
    return {"message": "User registered", user: user}


@router.post("/login")
@rate_limit(requests_limit=5, time_window=60)
def login(request: Request, data: LoginInput,
          session: Session = Depends(get_session)):
    token = AuthService.login(data.email, data.password, session)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
