from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

    @field_validator('email')
    def validate_email_format(cls, v):
        v = v.strip().lower()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError("Invalid email address format")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email_format(cls, v):
        return v.strip().lower()

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
