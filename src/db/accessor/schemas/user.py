from pydantic import BaseModel, EmailStr, validator
from uuid import UUID
from datetime import datetime
import re

# ---------- USER ----------
class Signup(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, value):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(pattern, value):
            raise ValueError("Password must be at least 8 characters long and include "
                              "an uppercase letter, a lowercase letter, a number, "
                              "and a special character (@$!%*?&)")
        return value
    class Config:
        from_attributes = True


class SignupResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class Login(BaseModel):
    email: EmailStr
    password: str
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
        uid: UUID
        username: str
        first_name: str
        last_name: str
        email: EmailStr
        role: str
        created_at: datetime
    
        class Config:
            from_attributes = True