"""
Admin Authentication Service
Handles admin user authentication with username/password
"""

import os
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from typing import Optional
from app.database import get_db_connection

# JWT settings
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Encode strings to bytes
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"❌ Error verifying password: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def create_admin_user(username: str, password: str) -> bool:
    """Create a new admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if username already exists
        cursor.execute(
            "SELECT id FROM admin_users WHERE username = ?",
            (username,)
        )
        if cursor.fetchone():
            conn.close()
            return False
        
        # Hash password and create user
        password_hash = get_password_hash(password)
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"❌ Error creating admin user: {str(e)}")
        return False


def authenticate_admin(username: str, password: str) -> Optional[dict]:
    """Authenticate admin user and return user info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, username, password_hash FROM admin_users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            conn.close()
            return None
        
        # Update last login
        cursor.execute(
            "UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        conn.commit()
        conn.close()
        
        return {
            "id": user['id'],
            "username": user['username']
        }
    except Exception as e:
        conn.close()
        print(f"❌ Error authenticating admin: {str(e)}")
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_admin_by_username(username: str) -> Optional[dict]:
    """Get admin user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, username, created_at, last_login FROM admin_users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    except Exception as e:
        conn.close()
        print(f"❌ Error getting admin user: {str(e)}")
        return None

