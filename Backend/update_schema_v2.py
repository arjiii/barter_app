import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SSL_CA_PATH = os.getenv("SSL_CA_PATH")

connect_args = {}
if SSL_CA_PATH:
    connect_args["ssl"] = {"ca": SSL_CA_PATH}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def update_schema():
    with engine.connect() as connection:
        # Add status to users
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
            print("Added status column to users table")
        except Exception as e:
            print(f"Error adding status to users (might already exist): {e}")

        # Add verification_method to pending_signups
        try:
            connection.execute(text("ALTER TABLE pending_signups ADD COLUMN verification_method VARCHAR(20) DEFAULT 'email'"))
            print("Added verification_method column to pending_signups table")
        except Exception as e:
            print(f"Error adding verification_method to pending_signups (might already exist): {e}")

        # Modify otp_code to be nullable in pending_signups
        # MySQL syntax
        try:
            connection.execute(text("ALTER TABLE pending_signups MODIFY otp_code VARCHAR(6) NULL"))
            print("Modified otp_code to be nullable in pending_signups table")
        except Exception as e:
            print(f"Error modifying otp_code in pending_signups: {e}")

        # Modify otp_expires_at to be nullable in pending_signups
        try:
            connection.execute(text("ALTER TABLE pending_signups MODIFY otp_expires_at DATETIME NULL"))
            print("Modified otp_expires_at to be nullable in pending_signups table")
        except Exception as e:
            print(f"Error modifying otp_expires_at in pending_signups: {e}")

if __name__ == "__main__":
    update_schema()
