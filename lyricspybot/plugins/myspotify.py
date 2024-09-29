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

from config import cache_chat
from lyricspybot import database
from lyricspybot.locales import use_chat_lang
from lyricspybot.utils import (
    get_current_track,
    get_song_art,
    get_spotify_session,
    get_track_info,
    http_client,
)

LFM_LINK_RE = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_inline_query(group=0)
@use_chat_lang()
async def my_spotify(c: Client, m: InlineQuery, t):
    spotify_session = await get_spotify_session(m.from_user.id)
    if not spotify_session or spotify_session.current_playback() is None:
        user_token = database.get(m.from_user.id)
        if not user_token or not user_token[2]:
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
        current_track = await get_current_track(user_token[2])
        if not current_track:
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
        track_info = await get_track_info(
            user_token[2], current_track[0]["artist"]["#text"], current_track[0]["name"]
        )
        use_sticker = database.theme(m.from_user.id)[3]
        message_text = (
            f"🎵 {current_track[0]['artist']['#text']} - {current_track[0]['name']}"
        )
        if use_sticker is None or use_sticker:
            album_url = current_track[0]["image"][-1]["#text"]
            if not album_url:
                response = await http_client.get(
                    current_track[0]["url"].replace("/_/", "/")
                )
                if response.status_code == 200:
                    album_url = LFM_LINK_RE.findall(response.text)[0]
                else:
                    fallback_response = await http_client.get(current_track[0]["url"])
                    album_url = LFM_LINK_RE.findall(fallback_response.text)[0]
            album_art = await get_song_art(
                song_name=current_track[0]["name"],
                artist_name=current_track[0]["artist"]["#text"],
                album_cover_url=album_url,
                theme_color="dark" if database.theme(m.from_user.id)[0] else "light",
                blur_background=database.theme(m.from_user.id)[1],
                play_count=track_info["track"]["userplaycount"],
                source="lastfm",
            )

            msg = await c.send_document(cache_chat, album_art, caption=message_text)

            article = [
                InlineQueryResultCachedDocument(
                    title=t("my_spotify"),
                    description=f'🎧 {current_track[0]["artist"]["#text"]} - {current_track[0]["name"]}',
                    id="MySpotify",
                    document_file_id=msg.sticker.file_id,
                    caption=message_text,
                )
            ]

        else:
            article = [
                InlineQueryResultArticle(
                    title=t("my_spotify"),
                    description=f'🎧 {current_track[0]["artist"]["#text"]} - {current_track[0]["name"]}',
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    input_message_content=InputTextMessageContent(
                        message_text=message_text,
                    ),
                )
            ]

    else:
        spotify_json = spotify_session.current_playback(
            additional_types="episode,track"
        )
        try:
            is_favorite = spotify_session.current_user_saved_tracks_contains([
                spotify_json["item"]["id"]
            ])[0]
        except SpotifyException:
            is_favorite = False
        if spotify_json["repeat_state"] == "track":
            repeat_emoji = "🔂"
            repeat_callback = f"sploopt|{m.from_user.id}"
        elif spotify_json["repeat_state"] == "context":
            repeat_emoji = "🔁"
            repeat_callback = f"sploopc|{m.from_user.id}"
        else:
            repeat_emoji = "↪️"
            repeat_callback = f"sploopo|{m.from_user.id}"
        if "artists" in spotify_json["item"]:
            publisher = spotify_json["item"]["artists"][0]["name"]
        else:
            publisher = spotify_json["item"]["show"]["name"]
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
                    InlineKeyboardButton(repeat_emoji, repeat_callback),
                ],
                [
                    InlineKeyboardButton(
                        f'{"❤" if is_favorite else ""} {spotify_json["item"]["name"]} - {publisher}',
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
        text = f'🎧 {spotify_json["item"]["name"]} - {publisher}\n'
        text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

        use_sticker = database.theme(m.from_user.id)[3]
        if use_sticker is None or use_sticker:
            album_art = await get_song_art(
                song_name=spotify_json["item"]["name"],
                artist_name=publisher,
                album_cover_url=spotify_json["item"]["album"]["images"][0]["url"]
                if "album" in spotify_json["item"]
                else spotify_json["item"]["images"][0]["url"],
                song_duration=spotify_json["item"]["duration_ms"] // 1000,
                playback_progress=spotify_json["progress_ms"] // 1000,
                theme_color="dark" if database.theme(m.from_user.id)[0] else "light",
                blur_background=database.theme(m.from_user.id)[1],
                source="lastfm",
            )

            msg = await c.send_document(cache_chat, album_art, caption=text)

            article = [
                InlineQueryResultCachedDocument(
                    title=t("my_spotify"),
                    description=f'🎧 {spotify_json["item"]["name"]} - {publisher}',
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
                    description=f'🎧 {spotify_json["item"]["name"]} - {publisher}',
                    id="MySpotify",
                    thumb_url="https://piics.ml/amn/lpy/spoti.png",
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text=(text),
                    ),
                )
            ]

    await m.answer(article, cache_time=0)


def get_repeat_info(spotify_json: dict, user_id: int):
    if spotify_json["repeat_state"] == "track":
        return "🔂", f"sploopt|{user_id}"
    if spotify_json["repeat_state"] == "context":
        return "🔁", f"sploopc|{user_id}"
    return "↪️", f"sploopo|{user_id}"


def get_publisher(spotify_json):
    return (
        spotify_json["item"]["artists"][0]["name"]
        if "artists" in spotify_json["item"]
        else spotify_json["item"]["show"]["name"]
    )


def get_player_keyboard(
    spotify_json, user_id, is_favorite, publisher, repeat_emoji, repeat_callback, t
):
    return [
        [
            ("⏮", f"spprevious|{user_id}"),
            (
                "⏸" if spotify_json["is_playing"] else "▶️",
                f"sppause|{user_id}"
                if spotify_json["is_playing"]
                else f"spplay|{user_id}",
            ),
            ("⏭", f"spnext|{user_id}"),
            (repeat_emoji, repeat_callback),
        ],
        [
            (
                f'{"❤" if is_favorite else ""} {spotify_json["item"]["name"]} - {publisher}',
                f'spmain|{user_id}|{spotify_json["item"]["id"]}',
            )
        ],
        [
            (t("top_button"), f"top|{user_id}"),
            (t("recent_button"), f"recently|{user_id}"),
        ],
    ]


def get_player_text(spotify_json, publisher):
    return (
        f'🎧 {spotify_json["item"]["name"]} - {publisher}\n'
        f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
    )


@Client.on_callback_query(
    filters.regex("^sp(previous|next|loopo|loopc|loopt|play|pause|main)")
)
@use_chat_lang()
async def update_playback_info(c: Client, m: CallbackQuery, t):
    action = m.matches[0].group(1)
    if m.data.split("|")[1] != str(m.from_user.id):
        user = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=user.first_name))
        return
    spotify_session = await get_spotify_session(m.from_user.id)
    if "premium" not in spotify_session.current_user()["product"]:
        await m.answer(t("premium_only"))
        return
    devices = spotify_session.devices()
    for device in devices["devices"]:
        if device["is_active"]:
            device_id = device["id"]
            break

    if action == "main":
        # this action is used only to update the player
        pass
    elif action == "previous":
        spotify_session.previous_track(device_id)
    elif action == "next":
        spotify_session.next_track(device_id)
    elif action in {"play", "pause"}:
        spotify_json = spotify_session.current_playback(
            additional_types="episode,track"
        )
        if spotify_json["is_playing"]:
            spotify_session.pause_playback(device_id)
        else:
            spotify_session.start_playback(device_id)
    elif action in {"loopo", "loopc", "loopt"}:
        if spotify_json["repeat_state"] == "context":
            spotify_session.repeat("track", device_id)
        elif spotify_json["repeat_state"] == "off":
            spotify_session.repeat("context", device_id)
        else:
            spotify_session.repeat("off", device_id)
    else:
        raise NameError(f"Unknown action name {action}")

    await asyncio.sleep(0.5)

    spotify_json = spotify_session.current_playback(additional_types="episode,track")
    try:
        is_favorite = spotify_session.current_user_saved_tracks_contains([
            spotify_json["item"]["id"]
        ])[0]
    except SpotifyException:
        is_favorite = False

    repeat_emoji, repeat_callback = get_repeat_info(spotify_json, m.from_user.id)
    publisher = get_publisher(spotify_json)

    keyboard = get_player_keyboard(
        spotify_json,
        m.from_user.id,
        is_favorite,
        publisher,
        repeat_emoji,
        repeat_callback,
        t,
    )
    text = get_player_text(spotify_json, publisher)

    await m.edit_message_text(text, reply_markup=ikb(keyboard))


@Client.on_callback_query(filters.regex("^recently|top"))
@use_chat_lang()
async def recently(c: Client, m: CallbackQuery, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        user = await c.get_chat(int(m.data.split("|")[1]))
        await m.answer(t("not_allowed").format(first_name=user.first_name))
        return
    spotify_session = await get_spotify_session(m.from_user.id)
    profile = spotify_session.current_user()
    if m.data.split("|")[0] == "recently":
        text = t("recent_text").format(name=profile["display_name"])
        track_list = spotify_session.current_user_recently_played(limit=10)
    else:
        text = t("top_text").format(name=profile["display_name"])
        track_list = spotify_session.current_user_top_tracks(limit=10)
    for index, item in enumerate(track_list["items"]):
        track = item.get("track", item)
        text += f'{index + 1}. {track["artists"][0]["name"]} - {track["name"]}\n'

    spotify_json = spotify_session.current_playback(additional_types="episode,track")
    try:
        is_favorite = spotify_session.current_user_saved_tracks_contains([
            spotify_json["item"]["id"]
        ])[0]
    except SpotifyException:
        is_favorite = False

    repeat_emoji, repeat_callback = get_repeat_info(spotify_json, m.from_user.id)
    publisher = get_publisher(spotify_json)
    keyboard = get_player_keyboard(
        spotify_json,
        m.from_user.id,
        is_favorite,
        publisher,
        repeat_emoji,
        repeat_callback,
        t,
    )

    await m.edit_message_text(text, reply_markup=ikb(keyboard))
