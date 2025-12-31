"""
Database initialization and connection
"""

import sqlite3
from pathlib import Path
from datetime import datetime


# Database file path
DB_PATH = Path("data/fitness.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn


def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clerk_user_id TEXT UNIQUE NOT NULL,
            email TEXT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create classifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            body_type TEXT NOT NULL,
            gender TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create fitness_plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fitness_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            classification_id INTEGER NOT NULL,
            workout_plan TEXT,
            meal_plan TEXT,
            plan_version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (classification_id) REFERENCES classifications(id)
        )
    """)
    
    # Create admin_users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def create_user(clerk_user_id: str, email: str = None, name: str = None):
    """Create or get user by Clerk ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute(
        "SELECT id FROM users WHERE clerk_user_id = ?",
        (clerk_user_id,)
    )
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return existing['id']
    
    # Create new user
    cursor.execute(
        "INSERT INTO users (clerk_user_id, email, name) VALUES (?, ?, ?)",
        (clerk_user_id, email, name)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def save_classification(user_id: int, body_type: str, gender: str):
    """Save or update body type classification (updates latest if exists)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user has existing classification
    cursor.execute(
        """SELECT id FROM classifications 
           WHERE user_id = ? 
           ORDER BY created_at DESC 
           LIMIT 1""",
        (user_id,)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing classification
        classification_id = existing['id']
        cursor.execute(
            """UPDATE classifications 
               SET body_type = ?, gender = ?, created_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (body_type, gender, classification_id)
        )
        print(f"✅ Updated existing classification ID: {classification_id}")
    else:
        # Create new classification
        cursor.execute(
            """INSERT INTO classifications (user_id, body_type, gender)
               VALUES (?, ?, ?)""",
            (user_id, body_type, gender)
        )
        classification_id = cursor.lastrowid
        print(f"✅ Created new classification ID: {classification_id}")
    
    conn.commit()
    conn.close()
    return classification_id


def save_plans(user_id: int, classification_id: int, workout_plan: str, meal_plan: str):
    """Save or update fitness plans (updates latest if exists for this classification)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if plan exists for this classification
    cursor.execute(
        """SELECT id FROM fitness_plans 
           WHERE classification_id = ? 
           ORDER BY created_at DESC 
           LIMIT 1""",
        (classification_id,)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing plan
        plan_id = existing['id']
        cursor.execute(
            """UPDATE fitness_plans 
               SET workout_plan = ?, meal_plan = ?, created_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (workout_plan, meal_plan, plan_id)
        )
        print(f"✅ Updated existing plan ID: {plan_id}")
    else:
        # Create new plan
        cursor.execute(
            """INSERT INTO fitness_plans 
               (user_id, classification_id, workout_plan, meal_plan)
               VALUES (?, ?, ?, ?)""",
            (user_id, classification_id, workout_plan, meal_plan)
        )
        plan_id = cursor.lastrowid
        print(f"✅ Created new plan ID: {plan_id}")
    
    conn.commit()
    conn.close()
    return plan_id


def get_user_latest_plan(clerk_user_id: str):
    """Get user's latest fitness plan"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                f.id,
                f.workout_plan,
                f.meal_plan,
                f.created_at,
                c.body_type,
                c.gender,
                c.id as classification_id
            FROM fitness_plans f
            JOIN classifications c ON f.classification_id = c.id
            JOIN users u ON f.user_id = u.id
            WHERE u.clerk_user_id = ?
            ORDER BY f.created_at DESC
            LIMIT 1
        """, (clerk_user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    except Exception as e:
        print(f"❌ Database error in get_user_latest_plan: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return None instead of raising - let endpoint handle it
        return None


def get_user_classifications(clerk_user_id: str):
    """Get all user's classifications"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            c.id,
            c.body_type,
            c.gender,
            c.created_at
        FROM classifications c
        JOIN users u ON c.user_id = u.id
        WHERE u.clerk_user_id = ?
        ORDER BY c.created_at DESC
    """, (clerk_user_id,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def user_exists(clerk_user_id: str):
    """Check if user exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM users WHERE clerk_user_id = ?",
        (clerk_user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


# Admin functions
def get_all_users():
    """Get all users with their latest classification and plan info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            u.id,
            u.clerk_user_id,
            u.email,
            u.name,
            u.created_at,
            c.body_type,
            c.gender,
            c.created_at as classification_date,
            f.workout_plan,
            f.meal_plan,
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
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def update_user(clerk_user_id: str, email: str = None, name: str = None):
    """Update user information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically
    updates = []
    params = []
    
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    
    if not updates:
        conn.close()
        return False
    
    params.append(clerk_user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE clerk_user_id = ?"
    
    cursor.execute(query, params)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_user_from_db(clerk_user_id: str):
    """Delete user and all related data from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user_id first
        cursor.execute("SELECT id FROM users WHERE clerk_user_id = ?", (clerk_user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False
        
        user_id = user['id']
        
        # Delete in order (respecting foreign keys)
        # 1. Delete fitness plans
        cursor.execute("DELETE FROM fitness_plans WHERE user_id = ?", (user_id,))
        
        # 2. Delete classifications
        cursor.execute("DELETE FROM classifications WHERE user_id = ?", (user_id,))
        
        # 3. Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"❌ Error deleting user: {str(e)}")
        raise

