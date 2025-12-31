"""
Admin Authentication API
Endpoints for admin login and account management
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from app.services.admin_auth import (
    authenticate_admin,
    create_access_token,
    verify_token,
    create_admin_user,
    get_admin_by_username
)
from app.database import get_db_connection

router = APIRouter(prefix="/admin-auth", tags=["Admin Authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateAdminRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current admin from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    admin = get_admin_by_username(username)
    if admin is None:
        raise HTTPException(status_code=401, detail="Admin user not found")
    
    return admin


@router.post("/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """Login as admin with username and password"""
    admin = authenticate_admin(request.username, request.password)
    
    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
    access_token = create_access_token(
        data={"sub": admin["username"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=admin["username"]
    )


@router.post("/create-admin")
async def create_admin_account(request: CreateAdminRequest):
    """Create a new admin account (requires existing admin or first-time setup)"""
    # Check if any admin exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM admin_users")
    admin_count = cursor.fetchone()['count']
    conn.close()
    
    # Allow creation if no admins exist (first-time setup)
    # Otherwise, require authentication
    if admin_count > 0:
        raise HTTPException(
            status_code=403,
            detail="Admin accounts can only be created by existing admins or during first-time setup"
        )
    
    success = create_admin_user(request.username, request.password)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to create admin account. Username may already exist."
        )
    
    return {
        "success": True,
        "message": f"Admin account '{request.username}' created successfully"
    }


@router.get("/me")
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current admin information"""
    return {
        "success": True,
        "admin": {
            "id": current_admin["id"],
            "username": current_admin["username"],
            "created_at": current_admin["created_at"],
            "last_login": current_admin["last_login"]
        }
    }


@router.get("/verify")
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if the provided token is valid"""
    try:
        admin = get_current_admin(credentials)
        return {
            "valid": True,
            "username": admin["username"]
        }
    except HTTPException:
        return {
            "valid": False,
            "message": "Invalid or expired token"
        }

