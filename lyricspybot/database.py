import sqlite3


def send_telegraph_page(song_info: dict[str, str], content: str) -> str:
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
                                         access_token TEXT,
                                         refresh_token TEXT,
                                         inline_results TEXT,
                                         user TEXT,
                                         color INTEGER,
                                         blur INTEGER,
                                         pattern INTEGER,
                                         current INTEGER,
                                         lang TEXT)"""
)

database_cursor.execute(
    """CREATE TABLE IF NOT EXISTS saves (hash TEXT,
                                         url TEXT,
                                         tl TEXT,
                                         tlt TEXT)"""
)

database_cursor.execute(
    """CREATE TABLE IF NOT EXISTS approved (user_id INTEGER,
                                            user INTEGER,
                                            approved INTEGER,
                                            usages INTEGER,
                                            usage INTEGER,
                                            dates INTEGER)"""
)


def add_approved(
    user_id: int,
    user: int,
    approved: int,
    usages: int | None = None,
    usage: int | None = None,
    dates: int | None = None,
) -> None:
    if existing_record := get_approved(user_id, user):
        database_cursor.execute(
            "UPDATE approved SET approved = ?, usages = ?, usage = ?, dates = ? WHERE user_id = ? AND user = ?",
            (approved, usages, usage, dates or existing_record[3], user_id, user),
        )
    else:
        database_cursor.execute(
            "INSERT INTO approved (user_id, user, approved, usages, usage, dates) VALUES (?,?,?,?,?,?)",
            (user_id, user, approved, usages, usage, dates),
        )
    database.commit()


def get_approved(user_id: int, user: int) -> tuple[int, int, int, int] | None:
    database_cursor.execute(
        "SELECT approved, usages, usage, dates FROM approved WHERE user_id = ? AND user = ?",
        (user_id, user),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def get_all_approved(
    user_id: int,
) -> list[tuple[int, int, int, int, int, int, int]] | None:
    database_cursor.execute(
        "SELECT *, approved FROM approved WHERE user_id = ?", (user_id,)
    )
    try:
        return database_cursor.fetchall()
    except IndexError:
        return None


def add_hash(hash_value: str, song_data: dict[str, str]) -> None:
    database_cursor.execute("SELECT url FROM saves WHERE hash = ?", (hash_value,))
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


def get_url(hash_value: str) -> tuple[str, str, str] | None:
    database_cursor.execute(
        "SELECT url, tl, tlt FROM saves WHERE hash = ?", (hash_value,)
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def add_user_last(user_id: int, username: str) -> None:
    if get(user_id):
        database_cursor.execute(
            "UPDATE users SET user = ? WHERE user_id = ?", (username, user_id)
        )
    else:
        database_cursor.execute(
            "INSERT INTO users (user_id, user) VALUES (?,?)", (user_id, username)
        )
    database.commit()


def add_user(user_id: int, refresh_token: str, access_token: str) -> None:
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


def update_user(user_id: int, access_token: str) -> None:
    database_cursor.execute(
        "UPDATE users SET access_token = ? WHERE user_id = ?", (access_token, user_id)
    )
    database.commit()


def tem(user_id: int, json_data: str | dict | None = None) -> tuple[str] | None:
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
            "SELECT inline_results FROM users WHERE user_id = ?", (user_id,)
        )
        try:
            return database_cursor.fetchone()
        except IndexError:
            return None
    return None


def get(user_id: int) -> tuple[str, str, str] | None:
    database_cursor.execute(
        "SELECT access_token, refresh_token, user FROM users WHERE user_id = ?",
        (user_id,),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def def_theme(user_id: int, color: int, blur: int, pattern: int, current: int) -> None:
    database_cursor.execute(
        "UPDATE users SET color = ?, blur = ?, pattern = ?, current = ? WHERE user_id = ?",
        (color, blur, pattern, current, user_id),
    )
    database.commit()


def theme(user_id: int) -> tuple[int, int, int, int] | None:
    database_cursor.execute(
        "SELECT color, blur, pattern, current FROM users WHERE user_id = ?",
        (user_id,),
    )
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None


def db_set_lang(user_id: int, language: str) -> None:
    if db_get_lang(user_id):
        database_cursor.execute(
            "UPDATE users SET lang = ? WHERE user_id = ?", (language, user_id)
        )
    else:
        database_cursor.execute(
            "INSERT INTO users (user_id, lang) VALUES (?,?)", (user_id, language)
        )
    database.commit()


def db_get_lang(user_id: int) -> tuple[str] | None:
    database_cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    try:
        return database_cursor.fetchone()
    except IndexError:
        return None
