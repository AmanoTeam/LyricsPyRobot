from config import SPOTFY_CONFIG
from locales import langdict
import httpx
import spotipy
from spotipy.client import SpotifyException
from json import loads

from db import db, dbc

http = httpx.AsyncClient(http2=True)

def get_user(user):
    dbc.execute(
        "SELECT spotify FROM users WHERE user_id = (?)", (user,)
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None

def set_user(user, sp):
    db.execute(
        "UPDATE users SET spotify = ? WHERE user_id = ?", (str(sp), user)
    )
    db.commit()

def gen_lang_keyboard():
    langs = list(langdict)
    keyb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [
            (f"{lang['language_flag']} {lang['language_name']}",
              "set_lang " + langs[0],)
        ]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append((f"{lang['language_flag']} {lang['language_name']}",
                   "set_lang " + langs[0],))
            langs.pop(0)
        keyb.append(a)
    return keyb

async def gen_spotify_token(user_id, token):
    r = await http.post(
        "https://accounts.spotify.com/api/token",
        headers=dict(Authorization=f"Basic {SPOTFY_CONFIG['BASIC']}"),
        data=dict(
            grant_type="authorization_code",
            code=token,
            redirect_uri="https://lyricspy.amanoteam.com/go",
        ),
    )
    temp = {}
    b = r.json()
    if b.get("error"):
        return False, b["error"]
    else:
        temp["token"] = b["access_token"]
        temp["refresh"] = b["refresh_token"]
        set_user(user_id, temp)
        return True, b["access_token"]

async def get_spoti_session(user_id):
    usr = (get_user(user_id)[0]).replace("'", '"')
    sp = loads(usr)
    a = spotipy.Spotify(auth=sp["token"])
    try:
        a.devices()
        return a
    except SpotifyException:
        new_token = await refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a

async def refresh_token(user_id):
    usr = (get_user(user_id)[0]).replace("'", '"')
    sp = loads(usr)
    r = await http.post(
        "https://accounts.spotify.com/api/token",
        headers=dict(Authorization=f"Basic {SPOTFY_CONFIG['BASIC']}"),
        data=dict(grant_type="refresh_token", refresh_token=sp["refresh"]),
    )
    b = r.json()
    sp["token"] = b["access_token"]
    set_user(user_id, sp)
    return b["access_token"]