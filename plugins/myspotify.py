import asyncio
import datetime
import re

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultCachedDocument,
    InputTextMessageContent,
)
from spotipy.exceptions import SpotifyException

import db
from config import cache_chat
from locales import use_chat_lang
from utils import (
    get_current,
    get_song_art,
    get_spoti_session,
    get_track_info,
    http_pool,
)

LFM_LINK_RE = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_inline_query(group=0)
@use_chat_lang()
async def my_spotify(c: Client, m: InlineQuery, t):
    sess = await get_spoti_session(m.from_user.id)
    if not sess or sess.current_playback() is None:
        tk = db.get(m.from_user.id)
        if not tk or not tk[2]:
            article = [
                InlineQueryResultArticle(
                    title=t("my_spotify"),
                    description=t("no_login"),
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    input_message_content=InputTextMessageContent(
                        message_text=t("login"),
                    ),
                )
            ]
            await m.answer(article, cache_time=0)
            return
        a = await get_current(tk[2])
        if not a:
            article = [
                InlineQueryResultArticle(
                    title=t("my_spotify"),
                    description=t("no_playng"),
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    input_message_content=InputTextMessageContent(
                        message_text=t("play"),
                    ),
                )
            ]
            await m.answer(article, cache_time=0)
            return
        track_info = await get_track_info(tk[2], a[0]["artist"]["#text"], a[0]["name"])
        stick = db.theme(m.from_user.id)[3]
        mtext = f"🎵 {a[0]['artist']['#text']} - {a[0]['name']}"
        if stick is None or stick:
            album_url = a[0]["image"][-1]["#text"]
            if not album_url:
                r = await http_pool.get(a[0]["url"].replace("/_/", "/"))
                if r.status_code == 200:
                    album_url = LFM_LINK_RE.findall(r.text)[0]
                else:
                    r2 = await http_pool.get(a[0]["url"])
                    album_url = LFM_LINK_RE.findall(r2.text)[0]
            album_art = await get_song_art(
                song_name=a[0]["name"],
                artist=a[0]["artist"]["#text"],
                album_url=album_url,
                color="dark" if db.theme(m.from_user.id)[0] else "light",
                blur=db.theme(m.from_user.id)[1],
                scrobbles=track_info["track"]["userplaycount"],
            )

            msg = await c.send_document(cache_chat, album_art, caption=mtext)

            article = [
                InlineQueryResultCachedDocument(
                    title=t("my_spotify"),
                    description=f'🎧 {a[0]["artist"]["#text"]} - {a[0]["name"]}',
                    id="MySpotify",
                    document_file_id=msg.sticker.file_id,
                    caption=mtext,
                )
            ]

        else:
            article = [
                InlineQueryResultArticle(
                    title=t("my_spotify"),
                    description=f'🎧 {a[0]["artist"]["#text"]} - {a[0]["name"]}',
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    input_message_content=InputTextMessageContent(
                        message_text=mtext,
                    ),
                )
            ]

    else:
        spotify_json = sess.current_playback(additional_types="episode,track")
        try:
            fav = sess.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[
                0
            ]
        except SpotifyException:
            fav = False
        if spotify_json["repeat_state"] == "track":
            emoji = "🔂"
            call = f"sploopt|{m.from_user.id}"
        elif spotify_json["repeat_state"] == "context":
            emoji = "🔁"
            call = f"sploopc|{m.from_user.id}"
        else:
            emoji = "↪️"
            call = f"sploopo|{m.from_user.id}"
        if "artists" in spotify_json["item"]:
            publi = spotify_json["item"]["artists"][0]["name"]
        else:
            publi = spotify_json["item"]["show"]["name"]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton("⏮", f"spprevious|{m.from_user.id}"),
                    InlineKeyboardButton(
                        "⏸" if spotify_json["is_playing"] else "▶️",
                        f"sppause|{m.from_user.id}"
                        if spotify_json["is_playing"]
                        else f"spplay|{m.from_user.id}",
                    ),
                    InlineKeyboardButton("⏭", f"spnext|{m.from_user.id}"),
                    InlineKeyboardButton(emoji, call),
                ],
                [
                    InlineKeyboardButton(
                        f'{"❤" if fav else ""} {spotify_json["item"]["name"]} - {publi}',
                        f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
                    )
                ],
                [
                    InlineKeyboardButton(t("top_button"), f"top|{m.from_user.id}"),
                    InlineKeyboardButton(
                        t("recent_button"), f"recently|{m.from_user.id}"
                    ),
                ],
            ]
        )
        text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
        text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

        stick = db.theme(m.from_user.id)[3]
        if stick is None or stick:
            album_art = await get_song_art(
                song_name=spotify_json["item"]["name"],
                artist=publi,
                album_url=spotify_json["item"]["album"]["images"][0]["url"]
                if "album" in spotify_json["item"]
                else spotify_json["item"]["images"][0]["url"],
                duration=spotify_json["item"]["duration_ms"] // 1000,
                progress=spotify_json["progress_ms"] // 1000,
                color="dark" if db.theme(m.from_user.id)[0] else "light",
                blur=db.theme(m.from_user.id)[1],
            )

            msg = await c.send_document(cache_chat, album_art, caption=text)

            article = [
                InlineQueryResultCachedDocument(
                    title=t("my_spotify"),
                    description=f'🎧 {spotify_json["item"]["name"]} - {publi}',
                    id="MySpotify",
                    document_file_id=msg.sticker.file_id,
                    caption=text,
                    reply_markup=keyboard,
                )
            ]
        else:
            article = [
                InlineQueryResultArticle(
                    title=t("my_spotify"),
                    description=f'🎧 {spotify_json["item"]["name"]} - {publi}',
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text=(text),
                    ),
                )
            ]

    await m.answer(article, cache_time=0)
    return


# Player
@Client.on_callback_query(filters.regex("^spprevious"))
@use_chat_lang()
async def previous(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        a = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
        return
    sp = await get_spoti_session(m.from_user.id)
    if "premium" not in sp.current_user()["product"]:
        await m.answer(t("premium_only"))
        return
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            break
    sp.previous_track(device_id)
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    try:
        fav = sp.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[0]
    except SpotifyException:
        fav = False

    if spotify_json["repeat_state"] == "track":
        emoji = "🔂"
        call = f"sploopt|{m.from_user.id}"
    elif spotify_json["repeat_state"] == "context":
        emoji = "🔁"
        call = f"sploopc|{m.from_user.id}"
    else:
        emoji = "↪️"
        call = f"sploopo|{m.from_user.id}"
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ("⏮", f"spprevious|{m.from_user.id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}"
                if spotify_json["is_playing"]
                else f"spplay|{m.from_user.id}",
            ),
            ("⏭", f"spnext|{m.from_user.id}"),
            (emoji, call),
        ],
        [
            (
                f'{spotify_json["item"]["name"]} - {publi} {"❤" if fav else ""}',
                f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{m.from_user.id}"),
            (t("recent_button"), f"recently|{m.from_user.id}"),
        ],
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))
    return


@Client.on_callback_query(filters.regex("^spnext"))
@use_chat_lang()
async def next(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        a = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
        return
    sp = await get_spoti_session(m.from_user.id)
    if "premium" not in sp.current_user()["product"]:
        await m.answer(t("premium_only"))
        return
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            break
    sp.next_track(device_id)
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    try:
        fav = sp.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[0]
    except SpotifyException:
        fav = False

    if spotify_json["repeat_state"] == "track":
        emoji = "🔂"
        call = f"sploopt|{m.from_user.id}"
    elif spotify_json["repeat_state"] == "context":
        emoji = "🔁"
        call = f"sploopc|{m.from_user.id}"
    else:
        emoji = "↪️"
        call = f"sploopo|{m.from_user.id}"
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ("⏮", f"spprevious|{m.from_user.id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}"
                if spotify_json["is_playing"]
                else f"spplay|{m.from_user.id}",
            ),
            ("⏭", f"spnext|{m.from_user.id}"),
            (emoji, call),
        ],
        [
            (
                f'{spotify_json["item"]["name"]} - {publi} {"❤" if fav else ""}',
                f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{m.from_user.id}"),
            (t("recent_button"), f"recently|{m.from_user.id}"),
        ],
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))
    return


@Client.on_callback_query(filters.regex("^sploopo|sploopc|sploopt"))
@use_chat_lang()
async def sp_loop(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        a = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
        return
    sp = await get_spoti_session(m.from_user.id)
    if "premium" not in sp.current_user()["product"]:
        await m.answer(t("premium_only"))
        return
    spotify_json = sp.current_playback(additional_types="episode,track")
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            break
    if spotify_json["repeat_state"] == "context":
        sp.repeat("track", device_id)
        emoji = "🔂"
        callb = f"sploopt|{m.from_user.id}"
    elif spotify_json["repeat_state"] == "off":
        sp.repeat("context", device_id)
        emoji = "🔁"
        callb = f"sploopc|{m.from_user.id}"
    else:
        sp.repeat("off", device_id)
        emoji = "↪️"
        callb = f"sploopo|{m.from_user.id}"
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    try:
        fav = sp.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[0]
    except SpotifyException:
        fav = False

    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ("⏮", f"spprevious|{m.from_user.id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}"
                if spotify_json["is_playing"]
                else f"spplay|{m.from_user.id}",
            ),
            ("⏭", f"spnext|{m.from_user.id}"),
            (emoji, callb),
        ],
        [
            (
                f'{spotify_json["item"]["name"]} - {publi} {"❤" if fav else ""}',
                f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{m.from_user.id}"),
            (t("recent_button"), f"recently|{m.from_user.id}"),
        ],
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))
    return


@Client.on_callback_query(filters.regex("^recently|top"))
@use_chat_lang()
async def recently(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        a = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
        return
    sp = await get_spoti_session(m.from_user.id)
    profile = sp.current_user()
    if m.data.split("|")[0] == "recently":
        text = t("recent_text").format(name=profile["display_name"])
        li = sp.current_user_recently_played(limit=10)
    else:
        text = t("top_text").format(name=profile["display_name"])
        li = sp.current_user_top_tracks(limit=10)
    for n, i in enumerate(li["items"]):
        res = i.get("track", i)
        text += f'{n + 1}. {res["artists"][0]["name"]} - {res["name"]}\n'

    spotify_json = sp.current_playback(additional_types="episode,track")
    try:
        fav = sp.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[0]
    except SpotifyException:
        fav = False

    if spotify_json["repeat_state"] == "track":
        emoji = "🔂"
        call = f"sploopt|{m.from_user.id}"
    elif spotify_json["repeat_state"] == "context":
        emoji = "🔁"
        call = f"sploopc|{m.from_user.id}"
    else:
        emoji = "↪️"
        call = f"sploopo|{m.from_user.id}"
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ("⏮", f"spprevious|{m.from_user.id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}"
                if spotify_json["is_playing"]
                else f"spplay|{m.from_user.id}",
            ),
            ("⏭", f"spnext|{m.from_user.id}"),
            (emoji, call),
        ],
        [
            (
                f'{spotify_json["item"]["name"]} - {publi} {"❤" if fav else ""}',
                f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{m.from_user.id}"),
            (t("recent_button"), f"recently|{m.from_user.id}"),
        ],
    ]
    await m.edit_message_text(text, reply_markup=ikb(keyb))
    return


@Client.on_callback_query(filters.regex("^sppause|^spplay|^spmain"))
@use_chat_lang()
async def sp_playpause(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        sess = await get_spoti_session(m.from_user.id)
        sess.add_to_queue(uri=f'spotify:track:{m.data.split("|")[2]}')
        await m.answer(t("song_added"))
        return
    sp = await get_spoti_session(m.from_user.id)
    if "premium" not in sp.current_user()["product"]:
        await m.answer(t("not_premium"))
        return
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            break
    spotify_json = sp.current_playback(additional_types="episode,track")
    if m.data.split("|")[0] != "spmain":
        if spotify_json["is_playing"]:
            sp.pause_playback(device_id)
        else:
            sp.start_playback(device_id)
        await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    try:
        fav = sp.current_user_saved_tracks_contains([spotify_json["item"]["id"]])[0]
    except SpotifyException:
        fav = False

    if spotify_json["repeat_state"] == "track":
        emoji = "🔂"
        call = f"sploopt|{m.from_user.id}"
    elif spotify_json["repeat_state"] == "context":
        emoji = "🔁"
        call = f"sploopc|{m.from_user.id}"
    else:
        emoji = "↪️"
        call = f"sploopo|{m.from_user.id}"
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ("⏮", f"spprevious|{m.from_user.id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}"
                if spotify_json["is_playing"]
                else f"spplay|{m.from_user.id}",
            ),
            ("⏭", f"spnext|{m.from_user.id}"),
            (emoji, call),
        ],
        [
            (
                f'{spotify_json["item"]["name"]} - {publi} {"❤" if fav else ""}',
                f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{m.from_user.id}"),
            (t("recent_button"), f"recently|{m.from_user.id}"),
        ],
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))
    return
