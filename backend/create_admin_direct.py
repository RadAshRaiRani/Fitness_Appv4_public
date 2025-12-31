#!/usr/bin/env python3
"""
Direct script to create admin account
Usage: python create_admin_direct.py [username] [password]
"""

import sys
from app.database import init_database
from app.services.admin_auth import create_admin_user, get_admin_by_username

def main():
    """Create admin account"""
    # Initialize database
    init_database()
    
    # Get username and password from args or use defaults
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "admin"
    
    # Check if username exists
    existing = get_admin_by_username(username)
    if existing:
        print(f"⚠️  Username '{username}' already exists!")
        sys.exit(1)
    
    # Create admin
    print(f"Creating admin account '{username}'...")
    success = create_admin_user(username, password)
    
    if success:
        print(f"✅ Admin account '{username}' created successfully!")
        print(f"\nLogin credentials:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"\nLogin endpoint: POST http://localhost:8000/admin-auth/login")
    else:
        print("❌ Failed to create admin account!")
        sys.exit(1)

if __name__ == "__main__":
    main()

