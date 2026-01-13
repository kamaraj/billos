"""Authentication schemas."""
from pydantic import BaseModel
from typing import Optional


class UserLogin(BaseModel):
    """Login request schema."""
    phone: str
    password: str


class UserRegister(BaseModel):
    """Registration request schema."""
    phone: str
    password: str
    name: str
    business_name: str
    business_type: Optional[str] = "retail"
    gst_no: Optional[str] = None
    is_gst_enabled: bool = False


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    user_name: str
    role: str


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
