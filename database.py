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
            CREATE TABLE IF NOT EXISTS donor_stats (
                team_id INTEGER NOT NULL,
                fah_donor_id INTEGER NOT NULL,
                points INTEGER NOT NULL,
                wus INTEGER NOT NULL,
                PRIMARY KEY (team_id, fah_donor_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fah_accounts (
                fah_donor_id INTEGER PRIMARY KEY,
                slack_id TEXT NOT NULL,
                FOREIGN KEY (slack_id) REFERENCES users(slack_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMEMT,
                team_id INTEGER NOT NULL,
                fah_donor_id INTEGER NOT NULL,
                donor_name TEXT NOT NULL,
                points_delta INTEGER NOT NULL,
                wus_delta INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                slack_ts TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT
            )
        """)


def link_user(slack_id, fah_donor_id):
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT OR IGNORE INTO users (slack_id) VALUES (?)", (slack_id,))

        existing = conn.execute(
            """
            SELECT slack_id
            FROM fah_accounts
            WHERE fah_donor_id = ?
        """,
            (fah_donor_id,),
        ).fetchone()

        if existing:
            if existing[0] == slack_id:
                return "already_linked"
            else:
                return "claimed"

        conn.execute(
            """
            INSERT INTO fah_accounts (slack_id, fah_donor_id)
            VALUES (?, ?)
        """,
            (slack_id, fah_donor_id),
        )

        return "link_success"


def unlink_user(slack_id, fah_donor_id):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM fah_accounts
            WHERE slack_id = ? AND fah_donor_id = ?
        """,
            (slack_id, fah_donor_id),
        )

        return cursor.rowcount > 0


def get_accounts(slack_id):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT fah_donor_id
            FROM fah_accounts
            WHERE slack_id = ?
        """,
            (slack_id,),
        ).fetchall()
    return [row[0] for row in rows]


def get_slack_user(fah_donor_id):
    with sqlite3.connect(db_path) as conn:
        slack_id = conn.execute(
            """
            SELECT slack_id
            FROM fah_accounts
            WHERE fah_donor_id = ?
            """,
            (fah_donor_id,),
        ).fetchone()
    return slack_id[0] if slack_id else None


def update_donor_stats(team_id, fah_donor_id, points, wus):
    with sqlite3.connect(db_path) as conn:
        previous = conn.execute(
            """
            SELECT points, wus
            FROM donor_stats
            WHERE team_id = ? AND fah_donor_id = ?
        """,
            (team_id, fah_donor_id),
        ).fetchone()

        conn.execute(
            """
            INSERT INTO donor_stats (
                team_id, fah_donor_id, points, wus
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(team_id, fah_donor_id)
            DO UPDATE SET
                points = excluded.points,
                wus = excluded.wus
        """,
            (team_id, fah_donor_id, points, wus),
        )
        if previous is None:
            return None

        old_points, old_wus = previous

        return {
            "points": points - old_points,
            "wus": wus - old_wus
        }