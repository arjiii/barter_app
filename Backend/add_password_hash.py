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

def add_password_hash():
    with engine.connect() as connection:
        inspector = inspect(engine)
        
        print("Checking pending_signups table...")
        pending_columns = [col['name'] for col in inspector.get_columns('pending_signups')]
        print(f"Current columns: {', '.join(pending_columns)}")
        
        if 'password_hash' not in pending_columns:
            print("\nAdding password_hash column...")
            try:
                connection.execute(text("ALTER TABLE pending_signups ADD COLUMN password_hash VARCHAR(255) NOT NULL"))
                connection.commit()
                print("✓ Added password_hash column")
            except Exception as e:
                print(f"✗ Error adding password_hash: {e}")
        else:
            print("✓ password_hash column already exists")

if __name__ == "__main__":
    add_password_hash()
