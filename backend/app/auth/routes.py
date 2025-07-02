# backend/app/auth/routes.py
"""
Authentication routes - Updated with approval system
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.database.models import User, PendingUserNotification, UserStatus, UserRole
from app.auth.models import (
    UserCreate, UserLogin, Token, User as UserResponse, UserUpdate,
    PasswordChange, PendingUser, UserApprovalRequest, ADMIN_EMAIL
)

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)
auth_router = APIRouter()

@auth_router.post("/register")
async def register(
        user_data: UserCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    """Register a new user - they will be in pending status awaiting admin approval"""

    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    # Create new user with pending status
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        status=UserStatus.PENDING,
        role=UserRole.USER,
        is_active=False  # Inactive until approved
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create notification record
    notification = PendingUserNotification(
        user_id=db_user.id,
        admin_email=ADMIN_EMAIL
    )
    db.add(notification)
    db.commit()

    # Send notification email to admin in background
    background_tasks.add_task(
        email_service.send_registration_notification,
        ADMIN_EMAIL,
        user_data.email,
        user_data.username,
        db_user.id
    )

    logger.info(f"New user registered: {user_data.email} (ID: {db_user.id}) - Pending approval")

    return {
        "message": "Registration successful! Your account is pending administrator approval. You will receive an email notification once your account is reviewed.",
        "status": "pending_approval",
        "user_id": db_user.id
    }

@auth_router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - only approved users can login"""

    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check user status
    if user.status == UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending administrator approval. Please wait for approval notification.",
        )
    elif user.status == UserStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account registration was not approved. Please contact the administrator.",
        )
    elif user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended. Please contact the administrator.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact the administrator.",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Admin endpoints
@auth_router.get("/admin/pending-users", response_model=List[PendingUser])
async def get_pending_users(
        current_admin: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Get all users pending approval (admin only)"""

    pending_users = db.query(User).filter(
        User.status == UserStatus.PENDING
    ).order_by(User.created_at.desc()).all()

    return pending_users

@auth_router.post("/admin/approve-user")
async def approve_or_reject_user(
        approval_request: UserApprovalRequest,
        background_tasks: BackgroundTasks,
        current_admin: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Approve or reject a pending user (admin only)"""

    user = db.query(User).filter(User.id == approval_request.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in pending status"
        )

    if approval_request.action == "approve":
        user.status = UserStatus.APPROVED
        user.is_active = True
        user.approved_at = func.now()
        user.approved_by = current_admin.id

        # Send approval email
        background_tasks.add_task(
            email_service.send_approval_notification,
            user.email,
            user.username,
            True
        )

        logger.info(f"User approved: {user.email} by admin: {current_admin.email}")
        message = f"User {user.username} has been approved successfully"

    elif approval_request.action == "reject":
        user.status = UserStatus.REJECTED
        user.rejection_reason = approval_request.rejection_reason
        user.approved_by = current_admin.id

        # Send rejection email
        background_tasks.add_task(
            email_service.send_approval_notification,
            user.email,
            user.username,
            False,
            approval_request.rejection_reason
        )

        logger.info(f"User rejected: {user.email} by admin: {current_admin.email}")
        message = f"User {user.username} has been rejected"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'approve' or 'reject'"
        )

    db.commit()
    db.refresh(user)

    return {
        "message": message,
        "user_id": user.id,
        "action": approval_request.action,
        "status": user.status
    }

@auth_router.get("/admin/all-users", response_model=List[UserResponse])
async def get_all_users(
        current_admin: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Get all users with their status (admin only)"""

    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

@auth_router.put("/admin/user/{user_id}/status")
async def update_user_status(
        user_id: int,
        new_status: str,
        current_admin: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Update user status (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        user.status = UserStatus(new_status)
        if new_status == UserStatus.APPROVED:
            user.is_active = True
        elif new_status in [UserStatus.REJECTED, UserStatus.SUSPENDED]:
            user.is_active = False

        db.commit()
        db.refresh(user)

        logger.info(f"User status updated: {user.email} -> {new_status} by admin: {current_admin.email}")

        return {
            "message": f"User status updated to {new_status}",
            "user_id": user.id,
            "new_status": new_status
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value"
        )

# Regular user profile management
@auth_router.put("/profile", response_model=UserResponse)
async def update_profile(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update user profile"""

    # Check if email is already taken by another user
    if user_data.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Check if username is already taken by another user
    if user_data.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Update user data
    current_user.email = user_data.email
    current_user.username = user_data.username

    db.commit()
    db.refresh(current_user)

    return current_user

@auth_router.put("/change-password")
async def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Change user password"""

    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}

# Add required import
from sqlalchemy.sql import func