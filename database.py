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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fah_accounts (
                fah_donor_id INTEGER PRIMARY KEY,
                slack_id TEXT NOT NULL,
                FOREIGN KEY (slack_id) REFERENCES users(slack_id)
            )
        """)


def link_user(slack_id, fah_donor_id):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (slack_id) VALUES (?)",
            (slack_id,)
        )

        conn.execute("""
            INSERT INTO fah_accounts (slack_id, fah_donor_id)
            VALUES (?, ?)
        """, (slack_id, fah_donor_id))

