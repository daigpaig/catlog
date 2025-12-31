from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..database import engine
from ..models.db_models import UserProfileDB
from .schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    GoogleTokenRequest,
)
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from .dependencies import get_current_user
from .google_oauth import verify_google_token, get_google_auth_url
from datetime import timedelta
from ..config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login endpoint that returns access and refresh tokens."""
    with Session(engine) as session:
        # Find user by email
        statement = select(UserProfileDB).where(UserProfileDB.email == login_data.email)
        user = session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.netid})
        refresh_token = create_refresh_token(data={"sub": user.netid})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
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
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user.netid})
        refresh_token = create_refresh_token(data={"sub": user.netid})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserProfileDB = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        netid=current_user.netid,
        name=current_user.name,
        email=current_user.email,
        majors=current_user.majors,
        minors=current_user.minors,
    )


@router.post("/register")
async def register(register_data: RegisterRequest):
    """Register a new user. (You may want to add more validation/requirements)"""
    with Session(engine) as session:
        # Check if user already exists
        statement = select(UserProfileDB).where(UserProfileDB.email == register_data.email)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Generate netid from email (or you might want to require it separately)
        # For now, using email prefix as netid - adjust based on your needs
        netid = register_data.email.split("@")[0]
        
        # Check if netid already exists
        existing_netid = session.get(UserProfileDB, netid)
        if existing_netid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NetID already exists",
            )
        
        # Create new user
        hashed_password = get_password_hash(register_data.password)
        new_user = UserProfileDB(
            netid=netid,
            name=register_data.name,
            email=register_data.email,
            hashed_password=hashed_password,
            majors=[],
            minors=[],
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Return tokens
        access_token = create_access_token(data={"sub": new_user.netid})
        refresh_token = create_refresh_token(data={"sub": new_user.netid})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )


@router.get("/google/login")
async def google_login_url():
    """Get Google OAuth login URL."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    auth_url = get_google_auth_url()
    return {"auth_url": auth_url}


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(google_data: GoogleTokenRequest):
    """Handle Google OAuth callback - verify token and create/login user."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    
    # Verify Google token
    google_user = verify_google_token(google_data.token)
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    
    email = google_user.get('email')
    name = google_user.get('name', 'User')
    google_id = google_user.get('sub')
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )
    
    with Session(engine) as session:
        # Check if user exists by email
        statement = select(UserProfileDB).where(UserProfileDB.email == email)
        user = session.exec(statement).first()
        
        if user:
            # User exists, update name if needed and return tokens
            if name and user.name != name:
                user.name = name
                session.commit()
                session.refresh(user)
        else:
            # Create new user
            # Generate netid from email
            netid = email.split("@")[0]
            
            # Check if netid already exists (unlikely but possible)
            existing_netid = session.get(UserProfileDB, netid)
            if existing_netid:
                # Append number if conflict
                counter = 1
                while session.get(UserProfileDB, f"{netid}{counter}"):
                    counter += 1
                netid = f"{netid}{counter}"
            
            # Create user without password (OAuth users don't need password)
            # Use a placeholder hash - users can set password later if needed
            user = UserProfileDB(
                netid=netid,
                name=name,
                email=email,
                hashed_password=get_password_hash(""),  # Empty password for OAuth users
                majors=[],
                minors=[],
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.netid})
        refresh_token = create_refresh_token(data={"sub": user.netid})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

