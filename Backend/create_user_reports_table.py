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

def create_user_reports_table():
    """Create user_reports table"""
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = 'user_reports'
        """, (config['database'],))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("Creating user_reports table...")
            cursor.execute("""
                CREATE TABLE user_reports (
                    id VARCHAR(36) PRIMARY KEY,
                    reporter_id VARCHAR(36) NOT NULL,
                    reported_user_id VARCHAR(36) NOT NULL,
                    reason VARCHAR(50) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (reported_user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_reporter (reporter_id),
                    INDEX idx_reported_user (reported_user_id),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                )
            """)
            connection.commit()
            print("✓ user_reports table created successfully!")
        else:
            print("✓ user_reports table already exists")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_user_reports_table()
