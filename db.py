import sqlite3

db = sqlite3.connect("users.db")
dbc = db.cursor()

dbc.execute(
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,
                                         test INTEGER,
                                         lang,
                                         pro INTEGER)""")

dbc.execute(
    """CREATE TABLE IF NOT EXISTS spotify (user_id INTEGER PRIMARY KEY,
                                           access_token,
                                           refresh_token)"""
)

db.commit()
