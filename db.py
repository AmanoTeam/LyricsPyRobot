import sqlite3

db = sqlite3.connect("users.db")
dbc = db.cursor()

dbc.execute(
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
                                         test INTEGER,
                                         lang)""")

db.commit()
