import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SSL_CA_PATH = os.getenv("SSL_CA_PATH")

connect_args = {}
if SSL_CA_PATH:
    connect_args["ssl"] = {"ca": SSL_CA_PATH}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def complete_pending_signups_schema():
    with engine.connect() as connection:
        inspector = inspect(engine)
        
        print("Checking pending_signups table...")
        pending_columns = [col['name'] for col in inspector.get_columns('pending_signups')]
        print(f"Current columns: {', '.join(pending_columns)}\n")
        
        # Add otp_code if missing
        if 'otp_code' not in pending_columns:
            print("Adding otp_code column...")
            try:
                connection.execute(text("ALTER TABLE pending_signups ADD COLUMN otp_code VARCHAR(6) NULL"))
                connection.commit()
                print("✓ Added otp_code column")
            except Exception as e:
                print(f"✗ Error adding otp_code: {e}")
        else:
            print("✓ otp_code column already exists")
            
        # Add otp_expires_at if missing
        if 'otp_expires_at' not in pending_columns:
            print("Adding otp_expires_at column...")
            try:
                connection.execute(text("ALTER TABLE pending_signups ADD COLUMN otp_expires_at DATETIME NULL"))
                connection.commit()
                print("✓ Added otp_expires_at column")
            except Exception as e:
                print(f"✗ Error adding otp_expires_at: {e}")
        else:
            print("✓ otp_expires_at column already exists")
            
        # Add created_at if missing
        if 'created_at' not in pending_columns:
            print("Adding created_at column...")
            try:
                connection.execute(text("ALTER TABLE pending_signups ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                connection.commit()
                print("✓ Added created_at column")
            except Exception as e:
                print(f"✗ Error adding created_at: {e}")
        else:
            print("✓ created_at column already exists")
        
        print("\n--- Final Schema ---")
        pending_columns = [col['name'] for col in inspector.get_columns('pending_signups')]
        for col in pending_columns:
            print(f"  - {col}")

if __name__ == "__main__":
    complete_pending_signups_schema()
    print("\n✓ Schema update complete!")
