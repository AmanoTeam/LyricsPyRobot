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

import db
from config import login_url
from locales import use_chat_lang
from utils import get_song_art, get_spoti_session, get_token, musixmatch

from .letra import letra


@Client.on_message(filters.service)
@use_chat_lang()
async def no(c: Client, m: Message, t):
    code = m.web_app_data.data
    print(code)
    res = await get_token(m.from_user.id, code)
    if res[0]:
        await m.reply_text(t("done"), reply_markup=ReplyKeyboardRemove())
    else:
        await m.reply_text(t("error").format(error=res[1]))


@Client.on_message(filters.command("start spoti_auto"), group=0)
@Client.on_callback_query(filters.regex("spoti_auto"))
@use_chat_lang()
async def spoti_auto(c: Client, m: Message | CallbackQuery, t):
    if isinstance(m, CallbackQuery):
        func = m.edit_message_text
    else:
        func = m.reply_text
    kb = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=t("automatic_login"), web_app=WebAppInfo(url=login_url)
                )
            ]
        ],
    )
    await func(t("automatic_text"), reply_markup=kb)


@Client.on_message(filters.command("start spoti_manual"), group=0)
@Client.on_callback_query(filters.regex("spoti_manual"))
@use_chat_lang()
async def spoti_manual(c: Client, m: Message | CallbackQuery, t):
    if isinstance(m, CallbackQuery):
        func = m.edit_message_text
    else:
        func = m.reply_text
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("manual_login"),
                    url=login_url,
                )
            ]
        ]
    )
    await func(t("manual_text"), reply_markup=kb)


@Client.on_message(filters.command("spoti"))
@use_chat_lang()
async def spoti(c: Client, m: Message, t):
    text = m.text.split(" ", 1)
    if len(text) == 2:
        access_code = text[1].split("code=")[1] if "code=" in text[1] else text[1]
        res = await get_token(m.from_user.id, access_code)
        if res[0]:
            await m.reply_text(t("done"), reply_markup=ReplyKeyboardRemove())
        else:
            await m.reply_text(t("error").format(error=res[1]))
    else:
        tk = db.get(m.from_user.id)
        if not tk or not tk[0]:
            if m.chat.type != ChatType.PRIVATE:
                dp_link = f"t.me/{c.me.username}?start="
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("automatic_login"),
                                url=dp_link + "spoti_auto",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=t("manual_login"),
                                url=dp_link + "spoti_manual",
                            )
                        ],
                    ]
                )
            else:
                kb = InlineKeyboardMarkup(
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
            await m.reply_text(t("login_txt"), reply_markup=kb)
        else:
            try:
                sess = await get_spoti_session(m.from_user.id)
            except Exception:
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("login"),
                                url=login_url,
                            )
                        ]
                    ]
                )
                await m.reply_text(t("login_txt"), reply_markup=kb)
                return
            spotify_json = sess.current_playback(additional_types="episode,track")
            try:
                fav = sess.current_user_saved_tracks_contains(
                    [spotify_json["item"]["id"]]
                )[0]
            except SpotifyException:
                fav = False
            if not spotify_json:
                await m.reply_text(t("play"))
            else:
                stick = db.theme(m.from_user.id)[3]
                if "artists" in spotify_json["item"]:
                    publi = spotify_json["item"]["artists"][0]["name"]
                else:
                    publi = spotify_json["item"]["show"]["name"]
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
                mtext = f"🎵 {publi} - {spotify_json['item']['name']}"
                if stick is None or stick:
                    mes = await m.reply_document(album_art, caption=mtext)
                else:
                    mes = await m.reply(
                        mtext,
                        parse_mode=ParseMode.HTML,
                    )
                await mes.react("❤" if fav else "")
                a = await musixmatch.spotify_lyrics(
                    artist=spotify_json["item"]["artists"][0]["name"],
                    track=spotify_json["item"]["name"],
                )
                if a:
                    m.text = "/letra spotify:" + str(
                        a["message"]["body"]["macro_calls"]["matcher.track.get"][
                            "message"
                        ]["body"]["track"]["track_id"]
                    )
                    try:
                        await letra(c, m)
                    except:
                        await m.reply_text(t("lyrics_nf"))
