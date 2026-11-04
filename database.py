
import sqlite3
from datetime import datetime, timezone

DATABASE_NAME = "matchi.db"


def connect():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                member_name TEXT NOT NULL,
                staff_id TEXT NOT NULL,
                staff_name TEXT NOT NULL,
                machine TEXT NOT NULL,
                prize TEXT NOT NULL,
                attempt_type TEXT NOT NULL,
                delivery_status TEXT DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)

        db.commit()


def save_attempt(
    member_id,
    member_name,
    staff_id,
    staff_name,
    machine,
    prize,
    attempt_type="Paid"
):
    with connect() as db:
        db.execute("""
            INSERT INTO attempts (
                member_id,
                member_name,
                staff_id,
                staff_name,
                machine,
                prize,
                attempt_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(member_id),
            member_name,
            str(staff_id),
            staff_name,
            machine,
            prize,
            attempt_type,
            datetime.now(timezone.utc).isoformat()
        ))

        db.commit()
