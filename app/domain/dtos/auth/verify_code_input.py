from pydantic import BaseModel


class VerifyCodeInput(BaseModel):
    email: str
    code: str
