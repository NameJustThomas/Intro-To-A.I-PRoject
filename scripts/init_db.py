"""
Database initialization script.
Runs SQL migrations to set up the database schema.
"""
import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def init_database():
    """Initialize database by running migration SQL files."""
    # Read migration file
    migration_file = Path(__file__).parent.parent / "infra" / "migrations" / "001_init.sql"
    
    if not migration_file.exists():
        print(f"Error: Migration file not found: {migration_file}")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute migration SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("Running database migration...")
        cursor.execute(migration_sql)
        
        print("Database initialized successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

