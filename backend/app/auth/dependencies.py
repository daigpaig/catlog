from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from ..database import engine
from ..models.db_models import UserProfileDB
from .security import verify_token
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfileDB:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    netid: str = payload.get("sub")
    if netid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    with Session(engine) as session:
        user = session.get(UserProfileDB, netid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserProfileDB]:
    """Dependency to optionally get the current user (for routes that work with or without auth)."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        return None
    
    netid: str = payload.get("sub")
    if netid is None:
        return None
    
    with Session(engine) as session:
        user = session.get(UserProfileDB, netid)
        return user

