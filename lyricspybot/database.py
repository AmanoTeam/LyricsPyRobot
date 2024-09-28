import sqlite3


def send_telegraph_page(song_info, content):
    from telegraph import Telegraph

    telegraph = Telegraph()
    telegraph.create_account(short_name="LyricsPyRobot", author_name="amn")
    response = telegraph.create_page(
        song_info["musica"],
        html_content=content.replace("\n", "<br>"),
        author_name=song_info["autor"],
        author_url=song_info["link"],
    )
    return response["url"]


database = sqlite3.connect("users.db")
database_cursor = database.cursor()

database_cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
                                         access_token,
                                         refresh_token,
                                         inline_results,
                                         user,
                                         color INTEGER,
                                         blur INTEGER,
                                         pattern INTEGER,
                                         current INTEGER,
                                         lang)"""
)

database_cursor.execute(
    """CREATE TABLE IF NOT EXISTS saves (hash,
                                         url,
                                         tl,
                                         tlt)"""
)

database_cursor.execute(
    """CREATE TABLE IF NOT EXISTS aproved (user_id INTEGER,
                                           user INTEGER,
                                           aproved INTEGER,
                                           usages INTEGER,
                                           uusage INTEGER,
                                           dates INTEGER)"""
)


def add_approved(user_id, user, approved, usages=None, uusage=None, dates=None):
    if existing_record := get_approved(user_id, user):
        database_cursor.execute(
            "UPDATE aproved SET aproved = ?, usages = ?, uusage = ?, dates = ? WHERE user_id = ? AND user = ?",
            (approved, usages, uusage, dates or existing_record[3], user_id, user),
        )
    else:
        database_cursor.execute(
            "INSERT INTO aproved (user_id, user, aproved, usages, uusage, dates) VALUES (?,?,?,?,?,?)",
            (user_id, user, approved, usages, uusage, dates),
        )
    database.commit()


def get_approved(user_id, user):
    database_cursor.execute(
        "SELECT aproved, usages, uusage, dates FROM aproved WHERE user_id = (?) AND user = (?)",
        (user_id, user),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def get_all_approved(user_id):
    database_cursor.execute(
        "SELECT *, aproved FROM aproved WHERE user_id = (?)", (user_id,)
    )
    try:
        return database_cursor.fetchall()
    except IndexError:
        return None


def add_hash(hash_value, song_data):
    database_cursor.execute("SELECT url FROM saves WHERE hash = (?)", (hash_value,))
    try:
        existing_url = database_cursor.fetchone()
    except IndexError:
        existing_url = None
    if not existing_url:
        telegraph_link = send_telegraph_page(song_data, song_data["letra"])
        translated_telegraph_link = (
            send_telegraph_page(song_data, song_data["traducao"])
            if song_data["traducao"]
            else ""
        )
        database_cursor.execute(
            "INSERT INTO saves (hash, url, tl, tlt) VALUES (?,?,?,?)",
            (hash_value, song_data["link"], telegraph_link, translated_telegraph_link),
        )
        database.commit()


def get_url(hash_value):
    database_cursor.execute(
        "SELECT url, tl, tlt FROM saves WHERE hash = (?)", (hash_value,)
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def add_user_last(user_id, username):
    if get(user_id):
        database_cursor.execute(
            "UPDATE users SET user = ? WHERE user_id = ?", (username, user_id)
        )
    else:
        database_cursor.execute(
            "INSERT INTO users (user_id, user) VALUES (?,?)", (user_id, username)
        )
    database.commit()


def add_user(user_id, refresh_token, access_token):
    if get(user_id):
        database_cursor.execute(
            "UPDATE users SET access_token = ? , refresh_token = ? , inline_results = ? WHERE user_id = ?",
            (access_token, refresh_token, "{}", user_id),
        )
    else:
        database_cursor.execute(
            "INSERT INTO users (user_id, access_token, refresh_token, inline_results) VALUES (?,?,?,?)",
            (user_id, access_token, refresh_token, "{}"),
        )
    database.commit()


def update_user(user_id, access_token):
    database_cursor.execute(
        "UPDATE users SET access_token = ? WHERE user_id = ?", (access_token, user_id)
    )
    database.commit()


def tem(user_id, json_data=None):
    if json_data:
        if not get(user_id):
            database_cursor.execute(
                "INSERT INTO users (user_id, inline_results) VALUES (?,?)",
                (user_id, str(json_data)),
            )
        else:
            print("tem")
            database_cursor.execute(
                "UPDATE users SET inline_results = ? WHERE user_id = ?",
                (str(json_data), user_id),
            )
        database.commit()
    else:
        database_cursor.execute(
            "SELECT inline_results FROM users WHERE user_id = (?)", (user_id,)
        )
        try:
            return database_cursor.fetchone()
        except IndexError:
            return None
    return None


def get(user_id):
    database_cursor.execute(
        "SELECT access_token, refresh_token, user FROM users WHERE user_id = (?)",
        (user_id,),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def def_theme(user_id, color, blur, pattern, current):
    database_cursor.execute(
        "UPDATE users SET color = ?, blur = ?, pattern = ?, current = ? WHERE user_id = ?",
        (color, blur, pattern, current, user_id),
    )
    database.commit()


def theme(user_id):
    database_cursor.execute(
        "SELECT color, blur, pattern, current FROM users WHERE user_id = (?)",
        (user_id,),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def db_set_lang(user_id, language):
    if db_get_lang(user_id):
        database_cursor.execute(
            "UPDATE users SET lang = ? WHERE user_id = ?", (language, user_id)
        )
    else:
        database_cursor.execute(
            "INSERT INTO users (user_id, lang) VALUES (?,?)", (user_id, language)
        )
    database.commit()


def db_get_lang(user_id):
    database_cursor.execute("SELECT lang FROM users WHERE user_id = (?)", (user_id,))
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None
