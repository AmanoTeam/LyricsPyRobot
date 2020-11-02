import sqlite3
from telegraph import Telegraph

telegraph = Telegraph()
telegraph.create_account(short_name='LyricsPyRobot', author_name='amn')


def send_te(a, b):
    response = telegraph.create_page(
        a['musica'].encode("latin-1", 'backslashreplace').decode("unicode_escape"),
        html_content=b.replace('\n', '<br>').encode("latin-1", 'backslashreplace').decode("unicode_escape"),
        author_name=a["autor"].encode("latin-1", 'backslashreplace').decode("unicode_escape"),
        author_url=a["link"].encode("latin-1", 'backslashreplace').decode("unicode_escape")
    )
    return response['url']


db = sqlite3.connect("users.db")
dbc = db.cursor()


dbc.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
                                                 access_token,
                                                 refresh_token,
                                                 inline_results,
                                                 user,
                                                 color)''')

dbc.execute('''CREATE TABLE IF NOT EXISTS saves (hash,
                                                 url,
                                                 tl,
                                                 tlt)''')


def add_hash(hash, h):
    dbc.execute('SELECT url FROM saves WHERE hash = (?)', (hash,))
    try:
        a = dbc.fetchone()
    except IndexError:
        a =  None
    if not a:
        tl = send_te(h, h['letra'])
        if 'traducao' in h:
            tlt = send_te(h, h['traducao'])
        else:
            tlt = ''
        dbc.execute('INSERT INTO saves (hash, url, tl, tlt) VALUES (?,?,?,?)',
                           (hash, h['link'],tl,tlt))
        db.commit()

def get_url(hash):
    dbc.execute('SELECT url, tl, tlt FROM saves WHERE hash = (?)', (hash,))
    try:
        return dbc.fetchone()
    except IndexError:
        return None

def add_user_last(id, user):
    if get(id):
        dbc.execute('UPDATE users SET user = ? WHERE user_id = ?', (user, id))
    else:
        dbc.execute('INSERT INTO users (user_id, user) VALUES (?,?)',
                               (id, user))
    db.commit()

def add_user(user, rtoken, atoken):
    if get(user):
        dbc.execute('UPDATE users SET access_token = ? , refresh_token = ? , inline_results = ? WHERE user_id = ?', 
                    (atoken, rtoken, '{}',user))
    else:
        dbc.execute('INSERT INTO users (user_id, access_token, refresh_token, inline_results) VALUES (?,?,?,?)',
                           (user, atoken, rtoken, '{}'))
    db.commit()
    
def update_user(user, atoken):
    dbc.execute('UPDATE users SET access_token = ? WHERE user_id = ?', (atoken, user))
    db.commit()

def tem(user_id, json=None):
    if json:
        if not get(user_id):
            dbc.execute('INSERT INTO users (user_id, inline_results) VALUES (?,?)',
                               (user_id, str(json)))
        else:
            print('tem')
            dbc.execute('UPDATE users SET inline_results = ? WHERE user_id = ?', (str(json), user_id))
        db.commit()
    else:
        dbc.execute('SELECT inline_results FROM users WHERE user_id = (?)', (user_id,))
        try:
            return dbc.fetchone()
        except IndexError:
            return None

def get(uid):
    dbc.execute('SELECT access_token, refresh_token, user FROM users WHERE user_id = (?)', (uid,))
    try:
        return dbc.fetchone()
    except IndexError:
        return None

def theme(uid):
    dbc.execute('SELECT color FROM users WHERE user_id = (?)', (uid,))
    try:
        return dbc.fetchone()[0]
    except IndexError:
        return None
