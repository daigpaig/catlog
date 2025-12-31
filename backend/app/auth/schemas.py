from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    netid: str
    name: str
    email: str
    majors: list[str]
    minors: Optional[list[str]] = None


class GoogleTokenRequest(BaseModel):
    token: str  # Google ID token from frontend

