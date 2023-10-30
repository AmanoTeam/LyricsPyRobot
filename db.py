import sqlite3


def send_te(a, b):
    from telegraph import Telegraph

    telegraph = Telegraph()
    telegraph.create_account(short_name="LyricsPyRobot", author_name="amn")
    response = telegraph.create_page(
        a["musica"],
        html_content=b.replace("\n", "<br>"),
        author_name=a["autor"],
        author_url=a["link"],
    )
    return response["url"]


db = sqlite3.connect("users.db")
dbc = db.cursor()

dbc.execute(
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

dbc.execute(
    """CREATE TABLE IF NOT EXISTS saves (hash,
                                         url,
                                         tl,
                                         tlt)"""
)

dbc.execute(
    """CREATE TABLE IF NOT EXISTS aproved (user_id INTEGER,
                                           user INTEGER,
                                           aproved INTEGER,
                                           usages INTEGER,
                                           uusage INTEGER,
                                           dates INTEGER)"""
)


def add_aproved(user_id, user, aproved, usages=None, uusage=None, dates=None):
    if get_aproved(user_id, user):
        dbc.execute(
            "UPDATE aproved SET aproved = ?, usages = ?, uusage = ?, dates = ? WHERE user_id = ? AND user = ?",
            (aproved, usages, uusage, dates, user_id, user),
        )
    else:
        dbc.execute(
            "INSERT INTO aproved (user_id, user, aproved, usages, uusage, dates) VALUES (?,?,?,?,?,?)",
            (user_id, user, aproved, usages, uusage, dates),
        )
    db.commit()


def get_aproved(user_id, user):
    dbc.execute(
        "SELECT aproved, usages, uusage, dates FROM aproved WHERE user_id = (?) AND user = (?)",
        (user_id, user),
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def get_all_aproved(user_id):
    dbc.execute("SELECT *, aproved FROM aproved WHERE user_id = (?)", (user_id,))
    try:
        return dbc.fetchall()
    except IndexError:
        return None


def add_hash(hash, h):
    dbc.execute("SELECT url FROM saves WHERE hash = (?)", (hash,))
    try:
        a = dbc.fetchone()
    except IndexError:
        a = None
    if not a:
        tl = send_te(h, h["letra"])
        if h["traducao"]:
            tlt = send_te(h, h["traducao"])
        else:
            tlt = ""
        dbc.execute(
            "INSERT INTO saves (hash, url, tl, tlt) VALUES (?,?,?,?)",
            (hash, h["link"], tl, tlt),
        )
        db.commit()


def get_url(hash):
    dbc.execute("SELECT url, tl, tlt FROM saves WHERE hash = (?)", (hash,))
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def add_user_last(id, user):
    if get(id):
        dbc.execute("UPDATE users SET user = ? WHERE user_id = ?", (user, id))
    else:
        dbc.execute("INSERT INTO users (user_id, user) VALUES (?,?)", (id, user))
    db.commit()


def add_user(user, rtoken, atoken):
    if get(user):
        dbc.execute(
            "UPDATE users SET access_token = ? , refresh_token = ? , inline_results = ? WHERE user_id = ?",
            (atoken, rtoken, "{}", user),
        )
    else:
        dbc.execute(
            "INSERT INTO users (user_id, access_token, refresh_token, inline_results) VALUES (?,?,?,?)",
            (user, atoken, rtoken, "{}"),
        )
    db.commit()


def update_user(user, atoken):
    dbc.execute("UPDATE users SET access_token = ? WHERE user_id = ?", (atoken, user))
    db.commit()


def tem(user_id, json=None):
    if json:
        if not get(user_id):
            dbc.execute(
                "INSERT INTO users (user_id, inline_results) VALUES (?,?)",
                (user_id, str(json)),
            )
        else:
            print("tem")
            dbc.execute(
                "UPDATE users SET inline_results = ? WHERE user_id = ?",
                (str(json), user_id),
            )
        db.commit()
    else:
        dbc.execute("SELECT inline_results FROM users WHERE user_id = (?)", (user_id,))
        try:
            return dbc.fetchone()
        except IndexError:
            return None


def get(uid):
    dbc.execute(
        "SELECT access_token, refresh_token, user FROM users WHERE user_id = (?)",
        (uid,),
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def def_theme(uid, color, blur, pattern, current):
    dbc.execute(
        "UPDATE users SET color = ?, blur = ?, pattern = ?, current = ? WHERE user_id = ?",
        (color, blur, pattern, current, uid),
    )
    db.commit()


def theme(uid):
    dbc.execute(
        "SELECT color, blur, pattern, current FROM users WHERE user_id = (?)", (uid,)
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None


def db_set_lang(id, user):
    if db_get_lang(id):
        dbc.execute("UPDATE users SET lang = ? WHERE user_id = ?", (user, id))
    else:
        dbc.execute("INSERT INTO users (user_id, lang) VALUES (?,?)", (id, user))
    db.commit()


def db_get_lang(uid):
    dbc.execute("SELECT lang FROM users WHERE user_id = (?)", (uid,))
    try:
        return dbc.fetchone()
    except IndexError:
        return None
