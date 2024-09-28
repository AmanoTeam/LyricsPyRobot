from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.enums.parse_mode import ParseMode
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)
from spotipy.exceptions import SpotifyException

from config import login_url
from lyricspybot import database
from lyricspybot.locales import use_chat_lang
from lyricspybot.plugins.letra import get_lyrics
from lyricspybot.utils import (
    get_song_art,
    get_spotify_session,
    get_token,
    musixmatch_client,
)


@Client.on_message(filters.service)
@use_chat_lang()
async def handle_web_app_data(c: Client, m: Message, t):
    authorization_code = m.web_app_data.data
    print(authorization_code)
    token_result = await get_token(m.from_user.id, authorization_code)
    if token_result[0]:
        await m.reply_text(t("done"), reply_markup=ReplyKeyboardRemove())
    else:
        await m.reply_text(t("error").format(error=token_result[1]))


@Client.on_message(filters.command("start spoti_auto"), group=0)
@Client.on_callback_query(filters.regex("spoti_auto"))
@use_chat_lang()
async def spoti_auto(c: Client, m: Message | CallbackQuery, t):
    response_function = (
        m.edit_message_text if isinstance(m, CallbackQuery) else m.reply_text
    )
    keyboard = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=t("automatic_login"), web_app=WebAppInfo(url=login_url)
                )
            ]
        ],
    )
    await response_function(t("automatic_text"), reply_markup=keyboard)


@Client.on_message(filters.command("start spoti_manual"), group=0)
@Client.on_callback_query(filters.regex("spoti_manual"))
@use_chat_lang()
async def spoti_manual(c: Client, m: Message | CallbackQuery, t):
    response_function = (
        m.edit_message_text if isinstance(m, CallbackQuery) else m.reply_text
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("manual_login"),
                    url=login_url,
                )
            ]
        ]
    )
    await response_function(t("manual_text"), reply_markup=keyboard)


@Client.on_message(filters.command("spoti"))
@use_chat_lang()
async def spoti(c: Client, m: Message, t):
    command_parts = m.text.split(" ", 1)
    if len(command_parts) == 2:
        access_code = (
            command_parts[1].split("code=")[1]
            if "code=" in command_parts[1]
            else command_parts[1]
        )
        token_result = await get_token(m.from_user.id, access_code)
        if token_result[0]:
            await m.reply_text(t("done"), reply_markup=ReplyKeyboardRemove())
        else:
            await m.reply_text(t("error").format(error=token_result[1]))
        return

    user_token = database.get(m.from_user.id)
    if not user_token or not user_token[0]:
        if m.chat.type != ChatType.PRIVATE:
            deep_link = f"t.me/{c.me.username}?start="
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("automatic_login"),
                            url=deep_link + "spoti_auto",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=t("manual_login"),
                            url=deep_link + "spoti_manual",
                        )
                    ],
                ]
            )
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("automatic_login"),
                            callback_data="spoti_auto",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=t("manual_login"),
                            callback_data="spoti_manual",
                        )
                    ],
                ]
            )
        await m.reply_text(t("login_txt"), reply_markup=keyboard)
    else:
        try:
            spotify_session = await get_spotify_session(m.from_user.id)
        except Exception:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("login"),
                            url=login_url,
                        )
                    ]
                ]
            )
            await m.reply_text(t("login_txt"), reply_markup=keyboard)
            return
        playback_info = spotify_session.current_playback(
            additional_types="episode,track"
        )
        try:
            is_favorite = spotify_session.current_user_saved_tracks_contains([
                playback_info["item"]["id"]
            ])[0]
        except SpotifyException:
            is_favorite = False
        if not playback_info:
            await m.reply_text(t("play"))
            return

        use_sticker = database.theme(m.from_user.id)[3]
        if "artists" in playback_info["item"]:
            publisher = playback_info["item"]["artists"][0]["name"]
        else:
            publisher = playback_info["item"]["show"]["name"]
        if use_sticker is None or use_sticker:
            album_art = await get_song_art(
                song_name=playback_info["item"]["name"],
                artist_name=publisher,
                album_cover_url=playback_info["item"]["album"]["images"][0]["url"]
                if "album" in playback_info["item"]
                else playback_info["item"]["images"][0]["url"],
                song_duration=playback_info["item"]["duration_ms"] // 1000,
                playback_progress=playback_info["progress_ms"] // 1000,
                theme_color="dark" if database.theme(m.from_user.id)[0] else "light",
                blur_background=database.theme(m.from_user.id)[1],
            )
        message_text = f"🎵 {publisher} - {playback_info['item']['name']}"
        if use_sticker is None or use_sticker:
            message = await m.reply_document(album_art, caption=message_text)
        else:
            message = await m.reply_text(
                message_text,
                parse_mode=ParseMode.HTML,
            )
        if is_favorite:
            await message.react("❤")
        lyrics_info = await musixmatch_client.spotify_lyrics(
            artist=playback_info["item"]["artists"][0]["name"],
            track=playback_info["item"]["name"],
        )
        if lyrics_info:
            m.text = "/letra spotify:" + str(
                lyrics_info["message"]["body"]["macro_calls"]["matcher.track.get"][
                    "message"
                ]["body"]["track"]["track_id"]
            )
            try:
                await get_lyrics(c, m)
            except Exception:
                await m.reply_text(t("lyrics_nf"))
