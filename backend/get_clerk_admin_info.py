#!/usr/bin/env python3
"""
Script to get Clerk admin user information
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ADMIN_CLERK_USER_ID = os.getenv("ADMIN_CLERK_USER_ID", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")

def get_clerk_user_info(user_id: str, secret_key: str):
    """Get user information from Clerk API"""
    if not secret_key or secret_key == "sk_test_xxxxx":
        print("⚠️  CLERK_SECRET_KEY is not properly configured in .env")
        print("   Please set your actual Clerk secret key to fetch user details.")
        return None
    
    try:
        url = f"https://api.clerk.com/v1/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        with httpx.Client() as client:
            response = client.get(url, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error fetching user: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("Clerk Admin User Information")
    print("=" * 60)
    
    if not ADMIN_CLERK_USER_ID:
        print("❌ ADMIN_CLERK_USER_ID not set in .env")
        return
    
    print(f"\nAdmin Clerk User ID: {ADMIN_CLERK_USER_ID}")
    print(f"Clerk Secret Key: {'✅ Set' if CLERK_SECRET_KEY and CLERK_SECRET_KEY != 'sk_test_xxxxx' else '❌ Not configured'}")
    
    if CLERK_SECRET_KEY and CLERK_SECRET_KEY != "sk_test_xxxxx":
        print("\nFetching user information from Clerk API...")
        user_info = get_clerk_user_info(ADMIN_CLERK_USER_ID, CLERK_SECRET_KEY)
        
        if user_info:
            print("\n✅ User Information:")
            print(f"   User ID: {user_info.get('id', 'N/A')}")
            print(f"   Email Addresses:")
            for email in user_info.get('email_addresses', []):
                print(f"     - {email.get('email_address', 'N/A')} {'(Primary)' if email.get('id') == user_info.get('primary_email_address_id') else ''}")
            print(f"   First Name: {user_info.get('first_name', 'N/A')}")
            print(f"   Last Name: {user_info.get('last_name', 'N/A')}")
            print(f"   Username: {user_info.get('username', 'N/A')}")
            print(f"   Created: {user_info.get('created_at', 'N/A')}")
        else:
            print("\n❌ Could not fetch user information")
    else:
        print("\n📝 To find your email:")
        print("   1. Go to https://dashboard.clerk.com")
        print("   2. Navigate to Users section")
        print("   3. Search for User ID: " + ADMIN_CLERK_USER_ID)
        print("   4. Click on the user to see their email address")
        print("\n   OR")
        print("   Log into your app at http://localhost:3000")
        print("   The email you used to sign in is your admin email")

if __name__ == "__main__":
    main()

