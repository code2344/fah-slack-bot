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
                notifications INTEGER DEFAULT 1
            )
        """)
def link_user(slack_id, fah_donor_id):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO users (slack_id, fah_donor_id)
            VALUES (?, ?)
            ON CONFLICT(slack_id)
            DO UPDATE SET fah_donor_id = excluded.fah_donor_id
        """, (slack_id, fah_donor_id))
