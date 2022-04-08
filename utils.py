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
        "SELECT access_token, refresh_token FROM spotify WHERE user_id = (?)", (user,)
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None

def set_user(user, access_token, refresh_token):
    if not get_user(user):
        dbc.execute(
            "INSERT INTO spotify (user_id, access_token, refresh_token) VALUES (?, ?, ?)",
            (user, access_token, refresh_token),
        )
    else:
        db.execute(
            "UPDATE spotify SET access_token = ?, refresh_token = ? WHERE user_id = ?", (access_token, refresh_token, user)
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
    b = r.json()
    if b.get("error"):
        return False, b["error"]
    else:
        print(b["access_token"], b["refresh_token"])
        set_user(user_id, b["access_token"], b["refresh_token"])
        return True, b["access_token"]

async def get_spoti_session(user_id):
    usr = get_user(user_id)[0]
    a = spotipy.Spotify(auth=usr)
    try:
        a.devices()
        return a
    except SpotifyException:
        new_token = await refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a

async def refresh_token(user_id):
    usr = get_user(user_id)[1]
    r = await http.post(
        "https://accounts.spotify.com/api/token",
        headers=dict(Authorization=f"Basic {SPOTFY_CONFIG['BASIC']}"),
        data=dict(grant_type="refresh_token", refresh_token=usr),
    )
    b = r.json()
    print(b)
    set_user(user_id, b["access_token"], usr)
    return b["access_token"]