#!/usr/bin/env python3
"""
Database Viewer Script
View and explore your fitness database data
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/fitness.db")


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def print_table(table_name, limit=10):
    """Print table contents"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"Table: {table_name} ({len(rows)} rows shown)")
    print(f"{'='*80}")
    
    if not rows:
        print("No data found")
        conn.close()
        return
    
    # Print header
    header = " | ".join(columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows:
        values = []
        for col in columns:
            val = row[col]
            if isinstance(val, str) and len(val) > 50:
                val = val[:47] + "..."
            values.append(str(val) if val is not None else "NULL")
        print(" | ".join(values))
    
    conn.close()


def view_all_users():
    """View all users with their classifications and plans"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            u.id,
            u.clerk_user_id,
            u.email,
            u.name,
            u.created_at as user_created,
            c.body_type,
            c.gender,
            c.created_at as classification_date,
            CASE WHEN f.id IS NOT NULL THEN 'Yes' ELSE 'No' END as has_plan,
            f.created_at as plan_date
        FROM users u
        LEFT JOIN classifications c ON u.id = c.user_id AND c.id = (
            SELECT id FROM classifications 
            WHERE user_id = u.id 
            ORDER BY created_at DESC 
            LIMIT 1
        )
        LEFT JOIN fitness_plans f ON c.id = f.classification_id AND f.id = (
            SELECT id FROM fitness_plans 
            WHERE classification_id = c.id 
            ORDER BY created_at DESC 
            LIMIT 1
        )
        ORDER BY u.created_at DESC
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n{'='*100}")
    print(f"ALL USERS SUMMARY ({len(rows)} users)")
    print(f"{'='*100}")
    
    if not rows:
        print("No users found")
        conn.close()
        return
    
    # Print header
    print(f"{'ID':<5} | {'Email':<30} | {'Name':<20} | {'Body Type':<12} | {'Gender':<8} | {'Has Plan':<10} | {'User Created'}")
    print("-" * 100)
    
    for row in rows:
        print(f"{row['id']:<5} | {str(row['email'] or 'N/A'):<30} | {str(row['name'] or 'N/A'):<20} | "
              f"{str(row['body_type'] or 'N/A'):<12} | {str(row['gender'] or 'N/A'):<8} | "
              f"{row['has_plan']:<10} | {row['user_created']}")
    
    conn.close()


def view_user_details(user_id=None, clerk_user_id=None):
    """View detailed information for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    elif clerk_user_id:
        cursor.execute("SELECT * FROM users WHERE clerk_user_id = ?", (clerk_user_id,))
    else:
        print("Please provide either user_id or clerk_user_id")
        conn.close()
        return
    
    user = cursor.fetchone()
    
    if not user:
        print("User not found")
        conn.close()
        return
    
    print(f"\n{'='*80}")
    print(f"USER DETAILS")
    print(f"{'='*80}")
    print(f"ID: {user['id']}")
    print(f"Clerk User ID: {user['clerk_user_id']}")
    print(f"Email: {user['email']}")
    print(f"Name: {user['name']}")
    print(f"Created: {user['created_at']}")
    
    # Get classifications
    cursor.execute("""
        SELECT * FROM classifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user['id'],))
    
    classifications = cursor.fetchall()
    print(f"\nClassifications ({len(classifications)}):")
    for cls in classifications:
        print(f"  - {cls['body_type']} ({cls['gender']}) - {cls['created_at']}")
    
    # Get plans
    cursor.execute("""
        SELECT f.*, c.body_type, c.gender 
        FROM fitness_plans f
        JOIN classifications c ON f.classification_id = c.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (user['id'],))
    
    plans = cursor.fetchall()
    print(f"\nFitness Plans ({len(plans)}):")
    for plan in plans:
        workout_len = len(plan['workout_plan'] or '')
        meal_len = len(plan['meal_plan'] or '')
        print(f"  - Plan ID: {plan['id']} | Body Type: {plan['body_type']} | "
              f"Workout: {workout_len} chars | Meal: {meal_len} chars | Created: {plan['created_at']}")
    
    conn.close()


def view_statistics():
    """View database statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"\n{'='*80}")
    print("DATABASE STATISTICS")
    print(f"{'='*80}")
    
    # Count users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    print(f"Total Users: {user_count}")
    
    # Count classifications
    cursor.execute("SELECT COUNT(*) as count FROM classifications")
    class_count = cursor.fetchone()['count']
    print(f"Total Classifications: {class_count}")
    
    # Count plans
    cursor.execute("SELECT COUNT(*) as count FROM fitness_plans")
    plan_count = cursor.fetchone()['count']
    print(f"Total Fitness Plans: {plan_count}")
    
    # Body type distribution
    cursor.execute("""
        SELECT body_type, COUNT(*) as count 
        FROM classifications 
        GROUP BY body_type
    """)
    print(f"\nBody Type Distribution:")
    for row in cursor.fetchall():
        print(f"  {row['body_type']}: {row['count']}")
    
    # Gender distribution
    cursor.execute("""
        SELECT gender, COUNT(*) as count 
        FROM classifications 
        WHERE gender IS NOT NULL
        GROUP BY gender
    """)
    print(f"\nGender Distribution:")
    for row in cursor.fetchall():
        print(f"  {row['gender']}: {row['count']}")
    
    # Users with plans
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) as count 
        FROM fitness_plans
    """)
    users_with_plans = cursor.fetchone()['count']
    print(f"\nUsers with Plans: {users_with_plans} / {user_count}")
    
    conn.close()


def main():
    """Main menu"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "users":
            view_all_users()
        elif command == "stats":
            view_statistics()
        elif command == "user":
            if len(sys.argv) > 2:
                user_id = sys.argv[2]
                try:
                    view_user_details(user_id=int(user_id))
                except ValueError:
                    view_user_details(clerk_user_id=user_id)
            else:
                print("Usage: python view_database.py user <user_id or clerk_user_id>")
        elif command == "tables":
            print_table("users")
            print_table("classifications")
            print_table("fitness_plans")
            print_table("admin_users")
        else:
            print(f"Unknown command: {command}")
    else:
        # Show menu
        print("\n" + "="*80)
        print("FITNESS DATABASE VIEWER")
        print("="*80)
        print("\nAvailable commands:")
        print("  python view_database.py stats          - Show database statistics")
        print("  python view_database.py users          - View all users summary")
        print("  python view_database.py user <id>      - View specific user details")
        print("  python view_database.py tables         - View all tables")
        print("\nOr use SQLite directly:")
        print("  sqlite3 data/fitness.db")
        print("\nExample SQL queries:")
        print("  SELECT * FROM users;")
        print("  SELECT * FROM classifications;")
        print("  SELECT * FROM fitness_plans;")
        
        # Show stats by default
        view_statistics()
        print("\n" + "="*80)


if __name__ == "__main__":
    main()
