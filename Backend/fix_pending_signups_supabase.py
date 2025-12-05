import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

# Parse DATABASE_URL
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not found in environment variables")

parsed = urlparse(database_url)

# MySQL connection config
config = {
    'host': parsed.hostname,
    'port': parsed.port or 3306,
    'user': parsed.username,
    'password': parsed.password,
    'database': parsed.path.lstrip('/'),
    'ssl_ca': os.getenv('SSL_CA_PATH'),
    'ssl_verify_cert': True,
    'ssl_verify_identity': True
}

def fix_pending_signups_supabase_field():
    """Make supabase_user_id nullable in pending_signups table"""
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Checking pending_signups table...")
        
        # Check if column exists
        cursor.execute("""
            SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'pending_signups'
            AND COLUMN_NAME = 'supabase_user_id'
        """, (config['database'],))
        
        result = cursor.fetchone()
        
        if result:
            print(f"Found supabase_user_id column: nullable={result[1]}, default={result[2]}")
            if result[1] == 'NO':
                print("Making supabase_user_id nullable...")
                cursor.execute("""
                    ALTER TABLE pending_signups 
                    MODIFY COLUMN supabase_user_id VARCHAR(255) NULL
                """)
                connection.commit()
                print("✓ supabase_user_id is now nullable!")
            else:
                print("✓ supabase_user_id is already nullable")
        else:
            print("supabase_user_id column doesn't exist, adding it...")
            cursor.execute("""
                ALTER TABLE pending_signups 
                ADD COLUMN supabase_user_id VARCHAR(255) NULL
            """)
            connection.commit()
            print("✓ supabase_user_id column added!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_pending_signups_supabase_field()
