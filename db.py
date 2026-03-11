import sqlite3
import logging

logger = logging.getLogger(__name__)

# Create table on first import
with sqlite3.connect("user_data.db") as _conn:
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS User_profile (
            Discord_ID INTEGER PRIMARY KEY,
            nametag TEXT NOT NULL,
            user_description TEXT
        );
    """)


def sqlite_conn(func):
    def wrapper(*args, **kwargs):
        with sqlite3.connect("user_data.db") as conn:
            cursor = conn.cursor()
            return func(cursor=cursor, *args, **kwargs)
    return wrapper


@sqlite_conn
def reg_user(*, cursor, discord_id: int, valorant_nametag: str, user_description: str) -> bool:
    try:
        cursor.execute(
            "INSERT INTO User_profile VALUES (?, ?, ?)",
            (discord_id, valorant_nametag, user_description)
        )
        return True
    except sqlite3.IntegrityError:
        # User already exists
        return False


@sqlite_conn
def edit_user(*, cursor, discord_id: int, valorant_nametag: str = None, user_description: str = None) -> bool:
    try:
        if valorant_nametag:
            cursor.execute(
                "UPDATE User_profile SET nametag = ? WHERE Discord_ID = ?",
                (valorant_nametag, discord_id)
            )
        if user_description:
            cursor.execute(
                "UPDATE User_profile SET user_description = ? WHERE Discord_ID = ?",
                (user_description, discord_id)
            )
        return True
    except sqlite3.Error as e:
        logger.error(f"edit_user error: {e}")
        return False


@sqlite_conn
def show_table(*, cursor, discord_id: int) -> tuple | None:
    try:
        cursor.execute(
            "SELECT * FROM User_profile WHERE Discord_ID = ?",
            (discord_id,)
        )
        return cursor.fetchone()
    except sqlite3.OperationalError as e:
        logger.error(f"show_table error: {e}")
        return None