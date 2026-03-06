import sqlite3

# conn = sqlite3.connect("user_data.db")
# cursor = conn.cursor()
#
#
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS User_profile(
#     Discord_ID INTEGER PRIMARY KEY,
#     nametag TEXT NOT NULL,
#     user_description TEXT
# );
# """)


def sqlite_conn(func):
    def wrapper(*args, **kwargs):
        with sqlite3.connect("user_data.db") as conn:
            cursor = conn.cursor()
            return func(cursor=cursor, *args, **kwargs)
    return wrapper

@sqlite_conn
def reg_user(*, cursor, discord_id : int, valorant_nametag : str, user_description : str) -> bool :
    try:
        cursor.execute("INSERT INTO User_profile VALUES (?, ?, ?)", (discord_id, valorant_nametag, user_description))
        return True
    except sqlite3.IntegrityError:
        return False

@sqlite_conn
def edit_user(*, cursor, discord_id : int, valorant_nametag : str = None, user_description : str = None) -> bool :
    try:
        if valorant_nametag:
            cursor.execute("""
            UPDATE User_profile
            SET nametag = ?
            WHERE discord_id = ?;""", (valorant_nametag, discord_id))
        if user_description:
            cursor.execute("""
            UPDATE User_profile
            SET user_description = ?
            WHERE discord_id = ?;
            """, (user_description, discord_id))
        return True
    except sqlite3.IntegrityError:
        return False



@sqlite_conn
def show_table(*, cursor) -> list | None :
    try:
        cursor.execute("""
                       SELECT * FROM User_profile;
                       """)
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return None


edit_user(discord_id=12287655812, valorant_nametag="Xenyz#rizz", user_description="LFT main agenst are sova and sage")
print(show_table())