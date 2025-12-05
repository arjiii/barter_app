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

def fix_schema():
    with engine.connect() as connection:
        inspector = inspect(engine)
        
        # Check users table
        print("Checking users table...")
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"Current users columns: {', '.join(users_columns)}")
        
        if 'status' not in users_columns:
            print("Adding status column to users...")
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
                connection.commit()
                print("✓ Added status column")
            except Exception as e:
                print(f"✗ Error adding status: {e}")
        else:
            print("✓ status column already exists")
        
        # Check pending_signups table
        print("\nChecking pending_signups table...")
        try:
            pending_columns = [col['name'] for col in inspector.get_columns('pending_signups')]
            print(f"Current pending_signups columns: {', '.join(pending_columns)}")
            
            if 'verification_method' not in pending_columns:
                print("Adding verification_method column...")
                try:
                    connection.execute(text("ALTER TABLE pending_signups ADD COLUMN verification_method VARCHAR(20) DEFAULT 'email'"))
                    connection.commit()
                    print("✓ Added verification_method column")
                except Exception as e:
                    print(f"✗ Error adding verification_method: {e}")
            else:
                print("✓ verification_method column already exists")
                
            # Make otp fields nullable
            if 'otp_code' in pending_columns:
                print("Modifying otp_code to be nullable...")
                try:
                    connection.execute(text("ALTER TABLE pending_signups MODIFY COLUMN otp_code VARCHAR(6) NULL"))
                    connection.commit()
                    print("✓ Modified otp_code")
                except Exception as e:
                    print(f"✗ Error modifying otp_code: {e}")
                    
            if 'otp_expires_at' in pending_columns:
                print("Modifying otp_expires_at to be nullable...")
                try:
                    connection.execute(text("ALTER TABLE pending_signups MODIFY COLUMN otp_expires_at DATETIME NULL"))
                    connection.commit()
                    print("✓ Modified otp_expires_at")
                except Exception as e:
                    print(f"✗ Error modifying otp_expires_at: {e}")
                    
        except Exception as e:
            print(f"✗ Error checking pending_signups: {e}")

if __name__ == "__main__":
    fix_schema()
    print("\n✓ Schema update complete!")
