import asyncio
import os
from functools import partial, wraps
from io import BytesIO
from time import time
from typing import Callable, Coroutine, List, Union

import httpx
import spotipy
from lyricspy.aio import Letras, Musixmatch
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from spotipy.client import SpotifyException
from yarl import URL

import db
from config import BASIC, BROWSER, KEY, MUSIXMATCH_KEYS

loop = asyncio.get_event_loop()

http_pool = httpx.AsyncClient(http2=True)


def aiowrap(fn: Callable) -> Coroutine:
    @wraps(fn)
    def decorator(*args, **kwargs):
        wrapped = partial(fn, *args, **kwargs)

        return loop.run_in_executor(None, wrapped)

    return decorator


@aiowrap
def get_song_art(
    song_name: str,
    artist: str,
    album_url: str,
    duration: int = 0,
    progress: int = 0,
    scrobbles: int = 0,
    color: str = "dark",
    blur: bool = False,
) -> BytesIO:
    params = dict(
        cover=album_url,
        track=song_name,
        artist=artist,
        timenow=progress,
        timetotal=duration,
        scrobbles=scrobbles,
        theme=color,
        blurbg=int(blur if blur is not None else True),
    )

    url = URL("https://lyricspy.amanoteam.com/nowplaying-dom/") % params

    webdrv.get(str(url))

    tmp_filename = f"{time()}.png"

    webdrv.save_screenshot(tmp_filename)

    img = Image.open(tmp_filename)

    bio = BytesIO()
    bio.name = "sticker.webp"

    img.save(bio)

    os.remove(tmp_filename)

    return bio


def build_webdriver_object(
    browser_type: str,
) -> Union[ChromeWebDriver, FirefoxWebDriver]:
    browser_type = browser_type.lower()

    if browser_type == "chrome":
        copts = webdriver.ChromeOptions()
        copts.headless = True

        webdrv_ = webdriver.Chrome(options=copts)
    elif browser_type == "firefox":
        fopts = webdriver.FirefoxOptions()
        fopts.headless = True
        fopts.add_argument("--kiosk")

        webdrv_ = webdriver.Firefox(options=fopts)
    else:
        raise TypeError("browser_type must be either 'chrome' or 'firefox'.")

    webdrv_.set_window_size(512, 288)

    return webdrv_


async def get_token(user_id, auth_code):
    r = await http_pool.post(
        "https://accounts.spotify.com/api/token",
        headers=dict(Authorization=f"Basic {BASIC}"),
        data=dict(
            grant_type="authorization_code",
            code=auth_code,
            redirect_uri="https://lyricspy.amanoteam.com/go",
        ),
    )
    b = r.json()
    if b.get("error"):
        return False, b["error"]
    else:
        print(b)
        db.add_user(user_id, b["refresh_token"], b["access_token"])
        return True, b["access_token"]


async def refresh_token(user_id):
    print("refreh")
    tk = db.get(user_id)
    print(tk[1])
    r = await http_pool.post(
        "https://accounts.spotify.com/api/token",
        headers=dict(Authorization=f"Basic {BASIC}"),
        data=dict(grant_type="refresh_token", refresh_token=tk[1]),
    )
    b = r.json()

    print(b)
    db.update_user(user_id, b["access_token"])
    return b["access_token"]


async def get_spoti_session(user_id) -> Union[spotipy.Spotify, bool]:
    tk = db.get(user_id)
    if not tk:
        return False
    a = spotipy.Spotify(auth=tk[0])
    try:
        a.devices()
        return a
    except SpotifyException:
        new_token = await refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a


async def get_current(user: str) -> List[dict]:
    r = await http_pool.get(
        "http://ws.audioscrobbler.com/2.0/",
        params=dict(
            method="user.getrecenttracks",
            user=user,
            api_key=KEY,
            format="json",
            limit=1,
        ),
    )
    return r.json()["recenttracks"]["track"]


async def get_track_info(user: str, artist: str, track: str):
    r = await http_pool.get(
        "http://ws.audioscrobbler.com/2.0/",
        params=dict(
            method="track.getInfo",
            user=user,
            api_key=KEY,
            format="json",
            artist=artist,
            track=track,
        ),
    )
    return r.json()


webdrv = build_webdriver_object(BROWSER)

musixmatch = Musixmatch(usertoken=MUSIXMATCH_KEYS)

letras = Letras()
