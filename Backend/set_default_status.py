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

def set_default_status():
    with engine.connect() as connection:
        # Set status='active' for all users that have NULL status
        print("Setting default status for existing users...")
        try:
            result = connection.execute(text("UPDATE users SET status = 'active' WHERE status IS NULL"))
            connection.commit()
            print(f"✓ Updated {result.rowcount} users with default status")
        except Exception as e:
            print(f"✗ Error updating status: {e}")

if __name__ == "__main__":
    set_default_status()
