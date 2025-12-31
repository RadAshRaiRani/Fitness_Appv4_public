"""
Admin API - User management endpoints
Requires admin authentication
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx

from app.database import (
    get_all_users,
    update_user,
    delete_user_from_db,
    get_user_latest_plan
)
from app.services.admin_auth import verify_token, get_admin_by_username

router = APIRouter()
security = HTTPBearer(auto_error=False)


def get_admin_clerk_user_id() -> str:
    """Get admin Clerk User ID from environment (read dynamically)"""
    return os.getenv("ADMIN_CLERK_USER_ID", "")


def verify_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Verify admin access - supports both Clerk User ID and JWT token authentication
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = credentials.credentials
    
    # First, try to verify as JWT token (username/password admin)
    payload = verify_token(token)
    if payload:
        username = payload.get("sub")
        if username:
            admin = get_admin_by_username(username)
            if admin:
                return {"type": "jwt", "username": username, **admin}
    
    # If not JWT, check if it's a Clerk User ID
    # Clerk User IDs start with "user_"
    if token.startswith("user_"):
        # Check if this Clerk User ID is the admin (read dynamically)
        admin_clerk_id = get_admin_clerk_user_id()
        if admin_clerk_id and token == admin_clerk_id:
            return {
                "type": "clerk",
                "clerk_user_id": token,
                "username": "clerk_admin"
            }
        else:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Admin privileges required."
            )
    
    # If neither JWT nor valid Clerk ID, deny access
    raise HTTPException(status_code=401, detail="Invalid or expired token")


class UpdateUserRequest(BaseModel):
    clerk_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None


class DeleteUserRequest(BaseModel):
    clerk_user_id: str


@router.get("/users")
async def list_all_users(current_admin: dict = Depends(verify_admin)):
    """Get all users in the system (admin only)"""
    
    try:
        users = get_all_users()
        return {
            "success": True,
            "count": len(users),
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{clerk_user_id}")
async def get_user_details(clerk_user_id: str, current_admin: dict = Depends(verify_admin)):
    """Get detailed information about a specific user (admin only)"""
    
    try:
        # Get user's latest plan which includes all info
        plan = get_user_latest_plan(clerk_user_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "clerk_user_id": clerk_user_id,
                "body_type": plan.get("body_type"),
                "gender": plan.get("gender"),
                "workout_plan": plan.get("workout_plan"),
                "meal_plan": plan.get("meal_plan"),
                "created_at": plan.get("created_at")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{clerk_user_id}")
async def update_user_info(
    clerk_user_id: str,
    request: UpdateUserRequest,
    current_admin: dict = Depends(verify_admin)
):
    """Update user information (admin only)"""
    
    if clerk_user_id != request.clerk_user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    try:
        updated = update_user(
            clerk_user_id=clerk_user_id,
            email=request.email,
            name=request.name
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": "User updated successfully",
            "clerk_user_id": clerk_user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{clerk_user_id}")
async def delete_user(clerk_user_id: str, current_admin: dict = Depends(verify_admin)):
    """Delete user from database and Clerk (admin only)"""
    
    try:
        # 1. Delete from database
        deleted_from_db = delete_user_from_db(clerk_user_id)
        
        if not deleted_from_db:
            raise HTTPException(status_code=404, detail="User not found in database")
        
        # 2. Delete from Clerk
        clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        if not clerk_secret_key:
            print("⚠️ WARNING: CLERK_SECRET_KEY not set. User deleted from database but not from Clerk.")
            return {
                "success": True,
                "message": "User deleted from database. Clerk deletion skipped (no API key).",
                "clerk_user_id": clerk_user_id
            }
        
        # Call Clerk API to delete user
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"https://api.clerk.com/v1/users/{clerk_user_id}",
                    headers={
                        "Authorization": f"Bearer {clerk_secret_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200 or response.status_code == 404:
                    print(f"✅ User deleted from Clerk: {clerk_user_id}")
                else:
                    print(f"⚠️ Clerk deletion returned status {response.status_code}: {response.text}")
        except Exception as clerk_error:
            print(f"⚠️ Error deleting from Clerk: {str(clerk_error)}")
            # Continue even if Clerk deletion fails - database deletion succeeded
        
        return {
            "success": True,
            "message": "User deleted from database and Clerk",
            "clerk_user_id": clerk_user_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check")
async def check_admin_status(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Check if the current user is an admin"""
    if not credentials:
        return {
            "is_admin": False,
            "message": "No authorization provided"
        }
    
    try:
        admin = verify_admin(credentials)
        return {
            "is_admin": True,
            "username": admin.get("username", "admin"),
            "type": admin.get("type", "unknown")
        }
    except HTTPException as e:
        return {
            "is_admin": False,
            "message": e.detail
        }


@router.get("/health")
async def admin_health():
    """Health check for admin API"""
    from app.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM admin_users")
    admin_count = cursor.fetchone()['count']
    conn.close()
    
    clerk_secret_key = os.getenv("CLERK_SECRET_KEY", "")
    
    admin_clerk_id = get_admin_clerk_user_id()
    
    return {
        "status": "healthy",
        "endpoint": "/api/v1/admin",
        "admin_accounts": admin_count,
        "clerk_admin_configured": bool(admin_clerk_id),
        "clerk_admin_user_id": admin_clerk_id if admin_clerk_id else None,
        "clerk_secret_key_configured": bool(clerk_secret_key) and clerk_secret_key != "sk_test_xxxxx",
        "auth_types": ["JWT (username/password)", "Clerk User ID"],
        "operations": [
            "GET /users - List all users",
            "GET /users/{clerk_user_id} - Get user details",
            "PUT /users/{clerk_user_id} - Update user",
            "DELETE /users/{clerk_user_id} - Delete user"
        ]
    }

