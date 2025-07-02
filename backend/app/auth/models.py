# backend/app/auth/models.py
"""
Pydantic models for authentication - Complete version with all required models
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

# Allowed email domains
ALLOWED_DOMAINS = ["@docaposte.fr", "@softeam.fr"]
ADMIN_EMAIL = "mohamed-ouassime.el-yamani@docaposte.fr"

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator('email')
    def validate_email_domain(cls, v):
        email_str = str(v)
        if not any(email_str.endswith(domain) for domain in ALLOWED_DOMAINS):
            allowed_domains_str = ", ".join(ALLOWED_DOMAINS)
            raise ValueError(f'Email must be from an allowed domain: {allowed_domains_str}')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: EmailStr
    username: str

    @validator('email')
    def validate_email_domain(cls, v):
        email_str = str(v)
        if not any(email_str.endswith(domain) for domain in ALLOWED_DOMAINS):
            allowed_domains_str = ", ".join(ALLOWED_DOMAINS)
            raise ValueError(f'Email must be from an allowed domain: {allowed_domains_str}')
        return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class User(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    status: UserStatus
    role: UserRole
    created_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PendingUser(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    status: UserStatus

    class Config:
        from_attributes = True

class UserApprovalRequest(BaseModel):
    user_id: int
    action: str  # "approve" or "reject"
    rejection_reason: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None