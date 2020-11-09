import asyncio
import os
from functools import wraps, partial
from io import BytesIO
from time import time
from typing import Coroutine, Callable, Union, List

import requests
import spotipy
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from spotipy.client import SpotifyException
from yarl import URL

import db
from config import BASIC, KEY, BROWSER

loop = asyncio.get_event_loop()


def aiowrap(fn: Callable) -> Coroutine:
    @wraps(fn)
    def decorator(*args, **kwargs):
        wrapped = partial(fn, *args, **kwargs)

        return loop.run_in_executor(None, wrapped)

    return decorator


@aiowrap
def get_song_art(song_name: str,
                 artist: str,
                 album_url: str,
                 duration: int = 0,
                 progress: int = 0,
                 color: str = "dark",
                 blur: bool = False) -> BytesIO:

    params = dict(cover=album_url,
                  track=song_name,
                  artist=artist,
                  timenow=progress,
                  timetotal=duration,
                  theme=color,
                  blurbg=int(blur))

    url = URL("https://lyricspy.amanoteam.com") / "nowplaying-dom" % params

    webdrv.get(str(url))

    tmp_filename = f"{time()}.png"

    webdrv.save_screenshot(tmp_filename)

    img = Image.open(tmp_filename)

    bio = BytesIO()
    bio.name = "sticker.webp"

    img.save(bio)

    os.remove(tmp_filename)

    return bio


def build_webdriver_object(browser_type: str) -> Union[ChromeWebDriver, FirefoxWebDriver]:
    browser_type = browser_type.lower()

    if browser_type == "chrome":
        copts = webdriver.ChromeOptions()
        copts.headless = True
        copts.add_argument("--window-size=512,288")

        webdrv = webdriver.Chrome(options=copts)
    elif browser_type == "firefox":
        fopts = webdriver.FirefoxOptions()
        fopts.headless = True
        fopts.add_argument("--width=512")
        fopts.add_argument("--height=288")

        webdrv = webdriver.Firefox(options=fopts)
    else:
        raise TypeError("browser_type must be either 'chrome' or 'firefox'.")

    return webdrv


def get_token(user_id, auth_code):
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {BASIC}"
                      ),
                      data=dict(
                          grant_type="authorization_code",
                          code=auth_code,
                          redirect_uri="https://lyricspy.amanoteam.com/go"
                      )).json()
    if b.get("error"):
        return False, b['error']
    else:
        print(b)
        db.add_user(user_id, b['refresh_token'], b['access_token'])
        return True, b['access_token']


def refresh_token(user_id):
    print('refreh')
    tk = db.get(user_id)
    print(tk[1])
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {BASIC}"
                      ),
                      data=dict(
                          grant_type="refresh_token",
                          refresh_token=tk[1]
                      )).json()
    print(b)
    db.update_user(user_id, b['access_token'])
    return b['access_token']


def get_current_playing(user_id) -> dict:
    tk = db.get(user_id)
    a = spotipy.Spotify(auth=tk[0])
    try:
        return a.current_user_playing_track()
    except SpotifyException:
        new_token = refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a.current_user_playing_track()


def get_current(user) -> List[dict]:
    r = requests.get('http://ws.audioscrobbler.com/2.0/', params=dict(
        method='user.getrecenttracks',
        user=user,
        api_key=KEY,
        format='json',
        limit=1))
    return r.json()['recenttracks']['track']


webdrv = build_webdriver_object(BROWSER)
