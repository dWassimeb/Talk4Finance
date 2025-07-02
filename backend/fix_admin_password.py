# backend/fix_admin_password.py
"""
Fix admin user password with proper bcrypt hashing
"""
import sqlite3
import os
import sys
sys.path.append('.')

DB_PATH = "powerbi_agent.db"

def fix_admin_password():
    """Update admin password with proper bcrypt hash"""

    try:
        # Import the proper hashing function
        from app.core.security import get_password_hash

        # New admin password
        new_password = "AdminPass123!"
        admin_email = "mohamed-ouassime.el-yamani@docaposte.fr"

        # Generate proper bcrypt hash
        print("🔧 Generating proper bcrypt hash...")
        hashed_password = get_password_hash(new_password)
        print(f"✓ Generated hash: {hashed_password[:50]}...")

        # Update database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Update admin password
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (hashed_password, admin_email)
        )

        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Updated password for {admin_email}")
            print(f"📝 You can now login with:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {new_password}")
        else:
            print(f"❌ Admin user not found: {admin_email}")

        conn.close()

    except ImportError as e:
        print(f"❌ Could not import security functions: {e}")
        print("Make sure you're running this from the backend directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Fixing Admin Password")
    print("=" * 30)
    fix_admin_password()