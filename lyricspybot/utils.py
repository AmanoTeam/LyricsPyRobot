import asyncio
import os
from io import BytesIO
from time import time

import httpx
import spotipy
from lyricspy.aio import Genius, Musixmatch
from PIL import Image
from playwright.async_api import BrowserContext, PlaywrightContextManager
from spotipy.client import SpotifyException
from yarl import URL

from config import BASIC, BROWSER, KEY, MUSIXMATCH_KEYS
from lyricspybot import database

http_client = httpx.AsyncClient(http2=True)


async def get_song_art(
    song_name: str,
    artist_name: str,
    album_cover_url: str,
    song_duration: int = 0,
    playback_progress: int = 0,
    play_count: int = 0,
    theme_color: str = "dark",
    blur_background: bool = False,
    source: str | None = None,
) -> BytesIO:
    request_params = {
        "cover": album_cover_url,
        "track": song_name,
        "artist": artist_name,
        "timenow": playback_progress,
        "timetotal": song_duration,
        "scrobbles": play_count,
        "theme": theme_color,
        "blurbg": int(blur_background if blur_background is not None else True),
        "source": source,
    }

    nowplaying_url = (
        URL("https://lyricspy.amanoteam.com/nowplaying-dom/") % request_params
    )

    browser_page = await browser.new_page()

    await browser_page.goto(str(nowplaying_url))

    screenshot_filename = f"{time()}.png"

    await browser_page.screenshot(path=screenshot_filename)

    await browser_page.close()

    screenshot_image = Image.open(screenshot_filename)

    sticker_file = BytesIO()
    sticker_file.name = "sticker.webp"

    screenshot_image.save(sticker_file)

    os.remove(screenshot_filename)

    return sticker_file


async def build_browser_object(browser_type: str) -> BrowserContext:
    browser_type = browser_type.lower()

    playwright_manager = await PlaywrightContextManager().start()

    if browser_type in {"chromium", "chrome"}:
        browser_instance = await playwright_manager.chromium.launch(headless=True)
    elif browser_type == "firefox":
        browser_instance = await playwright_manager.firefox.launch(headless=True)
    elif browser_type == "webkit":
        browser_instance = await playwright_manager.webkit.launch(headless=True)
    else:
        raise TypeError(
            "browser_type must be either 'chromium', 'firefox' or 'webkit'."
        )

    return await browser_instance.new_context(viewport={"width": 512, "height": 288})


async def get_token(user_id, auth_code):
    response = await http_client.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {BASIC}"},
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "https://lyricspy.amanoteam.com/go",
        },
    )
    response_data = response.json()
    if response_data.get("error"):
        return False, response_data["error"]
    print(response_data)
    database.add_user(
        user_id, response_data["refresh_token"], response_data["access_token"]
    )
    return True, response_data["access_token"]


async def refresh_token(user_id):
    print("refresh")
    user_tokens = database.get(user_id)
    print(user_tokens[1])
    response = await http_client.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {BASIC}"},
        data={"grant_type": "refresh_token", "refresh_token": user_tokens[1]},
    )
    response_data = response.json()

    print(response_data)
    database.update_user(user_id, response_data["access_token"])
    return response_data["access_token"]


async def get_spotify_session(user_id) -> spotipy.Spotify | None:
    user_tokens = database.get(user_id)
    if not user_tokens or not user_tokens[0]:
        return None
    spotify_client = spotipy.Spotify(auth=user_tokens[0])
    try:
        spotify_client.devices()
        return spotify_client
    except SpotifyException:
        new_access_token = await refresh_token(user_id)
        return spotipy.Spotify(auth=new_access_token)


async def get_current_track(user: str) -> list[dict]:
    response = await http_client.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "user.getrecenttracks",
            "user": user,
            "api_key": KEY,
            "format": "json",
            "limit": 1,
        },
    )
    return response.json()["recenttracks"]["track"]


async def get_track_info(user: str, artist: str, track: str):
    response = await http_client.get(
        "http://ws.audioscrobbler.com/2.0/",
        params={
            "method": "track.getInfo",
            "user": user,
            "api_key": KEY,
            "format": "json",
            "artist": artist,
            "track": track,
        },
    )
    return response.json()


event_loop = asyncio.new_event_loop()

browser = event_loop.run_until_complete(build_browser_object(BROWSER))

musixmatch_client = Musixmatch(usertoken=MUSIXMATCH_KEYS)

genius_client = Genius()
