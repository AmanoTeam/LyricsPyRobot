import asyncio
import os
from io import BytesIO
from time import time
from typing import Union

import httpx
import spotipy
from lyricspy.aio import Letras, Musixmatch
from PIL import Image
from playwright.async_api import BrowserContext, PlaywrightContextManager
from spotipy.client import SpotifyException
from yarl import URL

import db
from config import BASIC, BROWSER, KEY, MUSIXMATCH_KEYS

http_pool = httpx.AsyncClient(http2=True)


async def get_song_art(
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

    page = await browser.new_page()

    await page.goto(str(url))

    tmp_filename = f"{time()}.png"

    await page.screenshot(path=tmp_filename)

    await page.close()

    img = Image.open(tmp_filename)

    new_file = BytesIO()
    new_file.name = "sticker.webp"

    img.save(new_file)

    os.remove(tmp_filename)

    return new_file


async def build_browser_object(browser_type: str) -> BrowserContext:
    browser_type = browser_type.lower()

    p = await PlaywrightContextManager().start()

    if browser_type in {"chromium", "chrome"}:
        browser = await p.chromium.launch(headless=True)
    elif browser_type == "firefox":
        browser = await p.firefox.launch(headless=True)
    elif browser_type == "webkit":
        browser = await p.webkit.launch(headless=True)
    else:
        raise TypeError(
            "browser_type must be either 'chromium', 'firefox' or 'webkit'."
        )

    return await browser.new_context(viewport={"width": 512, "height": 288})


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


async def get_current(user: str) -> list[dict]:
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


loop = asyncio.new_event_loop()

browser = loop.run_until_complete(build_browser_object(BROWSER))

musixmatch = Musixmatch(usertoken=MUSIXMATCH_KEYS)

letras = Letras()
