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

def fix_pending_signups_expires_at():
    """Make expires_at nullable in pending_signups table"""
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Checking pending_signups table for expires_at column...")
        
        # Check if column exists
        cursor.execute("""
            SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_TYPE
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'pending_signups'
            AND COLUMN_NAME = 'expires_at'
        """, (config['database'],))
        
        result = cursor.fetchone()
        
        if result:
            print(f"Found expires_at column: nullable={result[1]}, default={result[2]}, type={result[3]}")
            if result[1] == 'NO':
                print("Making expires_at nullable...")
                cursor.execute("""
                    ALTER TABLE pending_signups 
                    MODIFY COLUMN expires_at DATETIME NULL
                """)
                connection.commit()
                print("✓ expires_at is now nullable!")
            else:
                print("✓ expires_at is already nullable")
        else:
            print("expires_at column doesn't exist - this is OK, we don't need it")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_pending_signups_expires_at()
