"""
Supabase configuration and client setup
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase credentials (get these from your Supabase project settings)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Create Supabase client
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Supabase client: {e}")
else:
    print("⚠ Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file")


def get_supabase_client() -> Client:
    """Get the Supabase client instance"""
    if not supabase:
        raise Exception("Supabase client not initialized. Check your credentials.")
    return supabase
