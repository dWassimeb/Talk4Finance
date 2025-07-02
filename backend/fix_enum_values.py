# backend/fix_enum_values.py
"""
Quick script to fix enum values in database
"""
import sqlite3
import os

DB_PATH = "powerbi_agent.db"

def fix_enum_values():
    """Convert lowercase enum values to uppercase"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("🔧 Fixing enum values...")

        # Check current values
        cursor.execute("SELECT email, status, role FROM users")
        users = cursor.fetchall()

        print("Current values:")
        for email, status, role in users:
            print(f"  {email}: status={status}, role={role}")

        # Update status values to uppercase
        status_mapping = {
            'pending': 'PENDING',
            'approved': 'APPROVED',
            'rejected': 'REJECTED',
            'suspended': 'SUSPENDED'
        }

        for old_status, new_status in status_mapping.items():
            cursor.execute(
                "UPDATE users SET status = ? WHERE status = ?",
                (new_status, old_status)
            )
            updated = cursor.rowcount
            if updated > 0:
                print(f"✓ Updated {updated} users from '{old_status}' to '{new_status}'")

        # Update role values to uppercase
        role_mapping = {
            'user': 'USER',
            'admin': 'ADMIN'
        }

        for old_role, new_role in role_mapping.items():
            cursor.execute(
                "UPDATE users SET role = ? WHERE role = ?",
                (new_role, old_role)
            )
            updated = cursor.rowcount
            if updated > 0:
                print(f"✓ Updated {updated} users from '{old_role}' to '{new_role}'")

        # Commit changes
        conn.commit()

        # Verify changes
        print("\nAfter fix:")
        cursor.execute("SELECT email, status, role FROM users")
        users = cursor.fetchall()

        for email, status, role in users:
            print(f"  {email}: status={status}, role={role}")

        print("✅ Enum values fixed!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_enum_values()