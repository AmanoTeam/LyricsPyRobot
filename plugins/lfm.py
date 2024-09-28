import re

from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.types import Message

import db
from locales import use_chat_lang
from utils import (
    get_current_track,
    get_song_art,
    get_track_info,
    http_client,
    musixmatch_client,
)

from .letra import get_lyrics

ALBUM_ART_REGEX = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_message(filters.command("lfm"))
@use_chat_lang()
async def last_fm_command(c: Client, m: Message, t):
    command_parts = m.text.split(" ", 1)
    if len(command_parts) == 2:
        db.add_user_last(m.from_user.id, command_parts[1])
        await m.reply_text(t("done"))
        return

    user_data = db.get(m.from_user.id)
    if not user_data or not user_data[2]:
        await m.reply_text(t("example"))
        return

    current_track = await get_current_track(user_data[2])
    if not current_track:
        await m.reply_text(t("play_playlist"))
        return

    track_info = await get_track_info(
        user_data[2], current_track[0]["artist"]["#text"], current_track[0]["name"]
    )

    message_text = (
        f"🎵 {current_track[0]['artist']['#text']} - {current_track[0]['name']}"
    )
    use_sticker = db.theme(m.from_user.id)[3]

    if use_sticker is None or use_sticker:
        album_url = await get_album_url(current_track[0])
        album_art = await get_song_art(
            song_name=current_track[0]["name"],
            artist_name=current_track[0]["artist"]["#text"],
            album_cover_url=album_url,
            theme_color="dark" if db.theme(m.from_user.id)[0] else "light",
            blur_background=db.theme(m.from_user.id)[1],
            play_count=track_info["track"]["userplaycount"],
        )
        await m.reply_document(album_art, caption=message_text)
    else:
        await m.reply_text(message_text, parse_mode=ParseMode.HTML)

    lyrics = await musixmatch_client.spotify_lyrics(
        artist=current_track[0]["artist"]["#text"], track=current_track[0]["name"]
    )
    if lyrics:
        m.text = f"/letra spotify:{lyrics['message']['body']['macro_calls']['matcher.track.get']['message']['body']['track']['track_id']}"
        try:
            await get_lyrics(c, m)
        except Exception:
            await m.reply_text(t("lyrics_nf"))


async def get_album_url(track_info):
    album_url = track_info["image"][-1]["#text"]
    if not album_url:
        response = await http_client.get(track_info["url"].replace("/_/", "/"))
        if response.status_code == 200:
            album_url = ALBUM_ART_REGEX.findall(response.text)[0]
        else:
            fallback_response = await http_client.get(track_info["url"])
            album_url = ALBUM_ART_REGEX.findall(fallback_response.text)[0]
    return album_url
