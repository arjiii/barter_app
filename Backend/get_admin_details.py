from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

with engine.connect() as connection:
    result = connection.execute(text("SELECT id, email, password_hash, supabase_user_id FROM users WHERE email = 'admin@bayanihan.com'"))
    admin = result.fetchone()
    
    if admin:
        print(f"Email: {admin.email}")
        print(f"Has Password Hash: {'Yes' if admin.password_hash else 'No'}")
        print(f"Has Supabase ID: {'Yes' if admin.supabase_user_id else 'No'}")
        if admin.password_hash:
            print(f"Password Hash (first 20 chars): {admin.password_hash[:20]}...")
