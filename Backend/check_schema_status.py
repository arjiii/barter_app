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

def check_schema():
    inspector = inspect(engine)
    
    print("=== USERS TABLE COLUMNS ===")
    try:
        columns = inspector.get_columns('users')
        for col in columns:
            nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
            print(f"  {col['name']}: {col['type']} ({nullable})")
        print(f"Total columns: {len(columns)}")
    except Exception as e:
        print(f"Error checking users table: {e}")
        
    print("\n=== PENDING_SIGNUPS TABLE COLUMNS ===")
    try:
        columns = inspector.get_columns('pending_signups')
        for col in columns:
            nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
            print(f"  {col['name']}: {col['type']} ({nullable})")
        print(f"Total columns: {len(columns)}")
    except Exception as e:
        print(f"Error checking pending_signups table: {e}")

if __name__ == "__main__":
    check_schema()
