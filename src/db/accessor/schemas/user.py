from pydantic import BaseModel, EmailStr, validator
from uuid import UUID
from datetime import datetime
import re

# ---------- USER ----------
class Signup(BaseModel):
    first_name: str
    last_name: str
    user_name: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, value):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(pattern, value):
            raise ValueError("Weak password")
        return value


class SignupResponse(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Login(BaseModel):
    email: EmailStr
    password: str
