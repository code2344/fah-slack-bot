import logging
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()
db_path = str(os.getenv("DB_PATH"))

logger = logging.getLogger(__name__)

def init_db():
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    slack_id TEXT PRIMARY KEY,
                    fah_donor_id TEXT NOT NULL,
                    fah_username TEXT NOT NULL,
                    notifications INTEGER DEFAULT 1
                )
            """)