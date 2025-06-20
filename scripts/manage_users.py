import argparse
import getpass
import secrets
import sys
import os
from passlib.context import CryptContext

# Add project root to path to allow importing backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.database import SessionLocal
from backend.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db_session, username, email, password):
    """Creates a new user in the database."""
    # Check if user already exists
    if db_session.query(User).filter(User.username == username).first():
        print(f"Error: User '{username}' already exists.")
        return
    if db_session.query(User).filter(User.email == email).first():
        print(f"Error: Email '{email}' is already in use.")
        return

    # Hash password
    password_hash = pwd_context.hash(password)

    # Generate API key and secret
    api_key = f"qk_{secrets.token_urlsafe(16)}"
    api_secret = secrets.token_urlsafe(32)
    api_secret_hash = pwd_context.hash(api_secret)

    # Create new user
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        api_key=api_key,
        api_secret_hash=api_secret_hash
    )

    db_session.add(new_user)
    db_session.commit()

    print("✅ User created successfully!")
    print("-" * 30)
    print(f"Username: {username}")
    print(f"Password: [hidden]")
    print(f"API Key: {api_key}")
    print(f"API Secret: {api_secret}")
    print("-" * 30)
    print("⚠️ This is the only time the API secret will be shown. Please store it securely.")


def main():
    parser = argparse.ArgumentParser(description="User management script for QuantX Exchange.")
    parser.add_argument("username", help="The username for the new user.")
    parser.add_argument("email", help="The email for the new user.")
    args = parser.parse_args()

    password = getpass.getpass("Enter password for the new user: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("❌ Passwords do not match.")
        sys.exit(1)

    db = SessionLocal()
    try:
        create_user(db, args.username, args.email, password)
    finally:
        db.close()

if __name__ == "__main__":
    main() 