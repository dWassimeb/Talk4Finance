# backend/migrate_database.py
"""
Simple database migration script for approval system
Database location: backend/powerbi_agent.db
"""
import sqlite3
import os
from datetime import datetime

# Database path - directly in backend folder
DB_PATH = "powerbi_agent.db"

def migrate_database():
    """Add approval system columns to existing database"""

    print(f"🔄 Starting migration for database: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        print(f"Current directory: {os.getcwd()}")
        print("Available files:", [f for f in os.listdir('.') if f.endswith('.db')])
        return False

    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Found tables: {tables}")

        if 'users' not in tables:
            print("❌ Users table not found!")
            return False

        # Check existing columns in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"✓ Existing columns: {columns}")

        # Add new columns if they don't exist
        new_columns = [
            ("status", "VARCHAR(20) DEFAULT 'approved'"),  # Set existing users as approved
            ("role", "VARCHAR(20) DEFAULT 'user'"),
            ("approved_at", "DATETIME"),
            ("approved_by", "INTEGER"),
            ("rejection_reason", "TEXT")
        ]

        for column_name, column_def in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                    print(f"✓ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠ Error adding {column_name}: {e}")
            else:
                print(f"⚠ Column {column_name} already exists")

        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                admin_email VARCHAR(255) NOT NULL,
                notification_sent BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created notifications table")

        # Set admin user (you) as admin role
        admin_email = "mohamed-ouassime.el-yamani@docaposte.fr"
        cursor.execute("""
            UPDATE users 
            SET status = 'approved', role = 'admin', approved_at = ? 
            WHERE email = ?
        """, (datetime.now().isoformat(), admin_email))

        admin_updated = cursor.rowcount
        if admin_updated > 0:
            print(f"✓ Set {admin_email} as admin")
        else:
            print(f"⚠ Admin user {admin_email} not found - will be created on first registration")

        # Approve all existing users
        cursor.execute("""
            UPDATE users 
            SET status = 'approved', approved_at = ? 
            WHERE status IS NULL OR status = ''
        """, (datetime.now().isoformat(),))

        approved_count = cursor.rowcount
        print(f"✓ Approved {approved_count} existing users")

        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")

        # Show final user count
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"📊 Total users in database: {total_users}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        conn.close()

def create_admin_if_needed():
    """Create admin user if database is empty"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if any users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            print("📝 No users found. Creating admin user...")

            # Simple password hashing (you should change this password immediately)
            import hashlib
            password = "AdminPass123!"
            # Simple hash - in production you'd use proper bcrypt
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, status, role, is_active, created_at, approved_at)
                VALUES (?, ?, ?, 'approved', 'admin', 1, ?, ?)
            """, (
                "mohamed-ouassime.el-yamani@docaposte.fr",
                "admin",
                hashed_password,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            print("✓ Created admin user")
            print("  Email: mohamed-ouassime.el-yamani@docaposte.fr")
            print("  Username: admin")
            print(f"  Password: {password}")
            print("  ⚠ CHANGE THIS PASSWORD IMMEDIATELY!")

    except Exception as e:
        print(f"⚠ Could not create admin user: {e}")
    finally:
        conn.close()

def verify_migration():
    """Verify the migration worked"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check users and their status
        cursor.execute("""
            SELECT email, username, status, role, is_active 
            FROM users 
            ORDER BY role DESC, email
        """)

        users = cursor.fetchall()
        print(f"\n📋 User Status Report:")
        print("-" * 60)

        for email, username, status, role, is_active in users:
            active_str = "✓" if is_active else "✗"
            print(f"{active_str} {email} | {username} | {status} | {role}")

        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM users 
            GROUP BY status
        """)

        print(f"\n📊 Status Summary:")
        for status, count in cursor.fetchall():
            print(f"  {status}: {count}")

    except Exception as e:
        print(f"⚠ Verification error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Simple Database Migration for Talk4Finance")
    print("=" * 50)

    # Run migration
    if migrate_database():
        # Create admin if needed
        create_admin_if_needed()

        # Verify results
        verify_migration()

        print(f"\n✅ Migration completed!")
        print(f"\nNext steps:")
        print(f"1. Restart your FastAPI application")
        print(f"2. Test login with your email")
        print(f"3. Check admin dashboard at /admin")
        print(f"4. Configure email settings in .env file")
    else:
        print(f"\n❌ Migration failed!")
        exit(1)