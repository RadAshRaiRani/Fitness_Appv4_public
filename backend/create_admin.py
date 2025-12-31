#!/usr/bin/env python3
"""
Script to create an admin account
Usage: python create_admin.py
"""

import sys
from app.database import init_database, get_db_connection
from app.services.admin_auth import create_admin_user, get_admin_by_username

def main():
    """Create admin account interactively"""
    print("=" * 60)
    print("Admin Account Creation")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Check if admin exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM admin_users")
    admin_count = cursor.fetchone()['count']
    conn.close()
    
    if admin_count > 0:
        print(f"\n⚠️  {admin_count} admin account(s) already exist(s).")
        response = input("Do you want to create another admin? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Get username
    username = input("\nEnter admin username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        sys.exit(1)
    
    # Check if username exists
    existing = get_admin_by_username(username)
    if existing:
        print(f"❌ Username '{username}' already exists!")
        sys.exit(1)
    
    # Get password
    password = input("Enter admin password: ").strip()
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    if len(password) < 6:
        print("⚠️  Warning: Password is less than 6 characters. Consider using a stronger password.")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    # Confirm password
    password_confirm = input("Confirm password: ").strip()
    if password != password_confirm:
        print("❌ Passwords do not match!")
        sys.exit(1)
    
    # Create admin
    print(f"\nCreating admin account '{username}'...")
    success = create_admin_user(username, password)
    
    if success:
        print(f"✅ Admin account '{username}' created successfully!")
        print("\nYou can now login at: POST /admin-auth/login")
        print("Example:")
        print(f'  curl -X POST "http://localhost:8000/admin-auth/login" \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"username": "{username}", "password": "YOUR_PASSWORD"}}\'')
    else:
        print("❌ Failed to create admin account!")
        sys.exit(1)

if __name__ == "__main__":
    main()

