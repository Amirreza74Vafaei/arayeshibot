import argparse
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal
from src.db import crud
from src.admin_panel.schemas import AdminUserCreate

def create_admin(username, password, role="admin"):
    """
    Creates a new admin user in the database.
    """
    print(f"Creating admin user: {username} with role: {role}")
    db = SessionLocal()

    # Check if user already exists
    existing_user = crud.get_admin_user_by_name(db, name=username)
    if existing_user:
        print(f"Error: Admin user '{username}' already exists.")
        db.close()
        return

    user_in = AdminUserCreate(
        name=username,
        password=password,
        role=role
    )

    try:
        crud.create_admin_user(db, user=user_in)
        print(f"Admin user '{username}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("username", type=str, help="The username for the new admin.")
    parser.add_argument("password", type=str, help="The password for the new admin.")
    parser.add_argument("--role", type=str, default="admin", help="The role for the new admin (e.g., 'admin', 'viewer').")

    args = parser.parse_args()

    create_admin(args.username, args.password, args.role)
