"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user
)
from app.core.config import settings
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, Token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user and create their business tenant."""
    
    # Check if phone already exists
    existing_user = db.query(User).filter(User.phone == data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create tenant (business)
    tenant = Tenant(
        name=data.business_name,
        business_type=data.business_type,
        gst_no=data.gst_no,
        is_gst_enabled=data.is_gst_enabled,
        plan="FREE"
    )
    db.add(tenant)
    db.flush()
    
    # Create user (owner)
    user = User(
        tenant_id=tenant.id,
        name=data.name,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role="OWNER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "tenant_id": tenant.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user_id=user.id,
        tenant_id=tenant.id,
        user_name=user.name,
        role=user.role
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login with phone and password."""
    
    user = db.query(User).filter(User.phone == data.phone).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        user_id=user.id,
        tenant_id=user.tenant_id,
        user_name=user.name,
        role=user.role
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id
    }
