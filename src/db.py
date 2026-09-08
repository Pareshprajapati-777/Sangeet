"""
Database connection and transaction manager for Sangeet.
Ensures parameterized queries, thread safety, and automatic schema initialization.
"""

import sqlite3
import logging
from contextlib import contextmanager
import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.config import DB_PATH, DATABASE_DIR

logger = logging.getLogger("sangeet.db")

def get_connection() -> sqlite3.Connection:
    """Returns a connection configured with dict-like row factories and foreign keys enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")  # High concurrency & speed
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB in-memory cache
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA mmap_size = 268435456;")  # 256MB fast memory-mapped I/O
    return conn

@contextmanager
def get_db():
    """Context manager for automatic commit and rollback."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Applies database/schema.sql to create canonical tables if not existing."""
    schema_path = DATABASE_DIR / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with get_db() as conn:
        conn.executescript(schema_sql)
    logger.info("Database initialized successfully at %s", DB_PATH)

if __name__ == "__main__":
    init_db()
    print(f"Database successfully initialized at: {DB_PATH}")
