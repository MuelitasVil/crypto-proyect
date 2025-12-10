from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class VerificationCode(SQLModel, table=True):
    __tablename__ = "verification_code"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=100)
    code: str = Field(max_length=6)
    created_at: datetime = (
        Field(default_factory=lambda: datetime.now(timezone.utc))
    )
    expires_at: datetime
    used: bool = Field(default=False)
