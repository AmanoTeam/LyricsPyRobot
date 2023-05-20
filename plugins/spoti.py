from pyrogram import Client, filters
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import db
from config import login_url
from locales import use_chat_lang
from utils import get_song_art, get_spoti_session, get_token

from .letra import letra


@Client.on_message(filters.command("spoti") | filters.command("np"))
@use_chat_lang()
async def spoti(c: Client, m: Message, t):
    text = m.text.split(" ", 1)
    if len(text) == 2:
        if "code=" in text[1]:
            access_code = text[1].split("code=")[1]
        else:
            access_code = text[1]
        res = await get_token(m.from_user.id, access_code)
        if res[0]:
            await m.reply_text(t("done"))
        else:
            await m.reply_text(t("error").format(error=res[1]))
    else:
        tk = db.get(m.from_user.id)
        if not tk or not tk[0]:
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
        else:
            sess = await get_spoti_session(m.from_user.id)
            spotify_json = sess.current_playback(additional_types="episode,track")
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
                if "np" in text[0]:
                    kb = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="⏮", callback_data=f"previous|{m.from_user.id}"
                                ),
                                InlineKeyboardButton(
                                    text="⏸" if spotify_json["is_playing"] else "▶️",
                                    callback_data=f"pause|{m.from_user.id}"
                                    if spotify_json["is_playing"]
                                    else f"play|{m.from_user.id}",
                                ),
                                InlineKeyboardButton(
                                    text="⏭", callback_data=f"next|{m.from_user.id}"
                                ),
                            ],
                            [
                                InlineKeyboardButton(
                                    text=t("play_in_sp"),
                                    callback_data=f'tcs|{spotify_json["item"]["id"]}',
                                ),
                                InlineKeyboardButton(
                                    text=t("search_lyric"),
                                    callback_data=f'sp_s|{spotify_json["item"]["id"]}|{m.from_user.id}',
                                ),
                            ],
                        ]
                    )
                    if stick is None or stick:
                        await m.reply_document(
                            album_art, reply_markup=kb, caption=mtext
                        )
                    else:
                        await m.reply(
                            mtext,
                            reply_markup=kb,
                            parse_mode=ParseMode.HTML,
                        )
                else:
                    if stick is None or stick:
                        await m.reply_document(album_art, caption=mtext)
                    else:
                        await m.reply(
                            mtext,
                            parse_mode=ParseMode.HTML,
                        )
                    m.text = f"/letra {spotify_json['item']['artists'][0]['name']} {spotify_json['item']['name']}"
                    await letra(c, m)


@Client.on_callback_query(filters.regex(r"^sp_s"))
async def sp_search(c: Client, m: CallbackQuery):
    track, uid = m.data.split("|")[1:]
    if m.from_user.id == int(uid):
        sess = await get_spoti_session(m.from_user.id)
        om = m.message
        om.from_user = m.from_user
        spotify_json = sess.track(track)
        om.text = f"/letra {spotify_json['artists'][0]['name']} {spotify_json['name']}"
        await letra(c, om)


@Client.on_callback_query(filters.regex(r"^tcs"))
@use_chat_lang()
async def tcs(c: Client, m: CallbackQuery, t):
    sess = await get_spoti_session(m.from_user.id)
    sess.add_to_queue(uri=f'spotify:track:{m.data.split("|")[1]}')
    await m.answer(t("song_added"))


@Client.on_callback_query(filters.regex(r"^previous"))
@use_chat_lang()
async def previous(c: Client, m: CallbackQuery, t):
    user = m.data.split("|")[1]
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        for i in devices["devices"]:
            if i["is_active"]:
                device_id = i["id"]
                break
        sess.previous_track(device_id)
        spotify_json = sess.current_playback(additional_types="episode,track")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏮", callback_data=f"previous|{m.from_user.id}"
                    ),
                    InlineKeyboardButton(
                        text="⏸" if spotify_json["is_playing"] else "▶️",
                        callback_data=f"pause|{m.from_user.id}"
                        if spotify_json["is_playing"]
                        else f"play|{m.from_user.id}",
                    ),
                    InlineKeyboardButton(
                        text="⏭", callback_data=f"next|{m.from_user.id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("play_in_sp"),
                        callback_data=f'tcs|{spotify_json["item"]["id"]}',
                    ),
                    InlineKeyboardButton(
                        text=t("search_lyric"),
                        callback_data=f'sp_s|{spotify_json["item"]["id"]}|{m.from_user.id}',
                    ),
                ],
            ]
        )
        if "artists" in spotify_json["item"]:
            publi = spotify_json["item"]["artists"][0]["name"]
        else:
            publi = spotify_json["item"]["show"]["name"]
        spotify_json = sess.current_playback(additional_types="episode,track")
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(
                f"🎵 {publi} - {spotify_json['item']['name']}",
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
        else:
            await m.answer(f"🎵 {publi} - {spotify_json['item']['name']}")
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^next"))
@use_chat_lang()
async def next(c: Client, m: CallbackQuery, t):
    user = m.data.split("|")[1]
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        for i in devices["devices"]:
            if i["is_active"]:
                device_id = i["id"]
                break
        sess.next_track(device_id)
        spotify_json = sess.current_playback(additional_types="episode,track")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏮", callback_data=f"previous|{m.from_user.id}"
                    ),
                    InlineKeyboardButton(
                        text="⏸" if spotify_json["is_playing"] else "▶️",
                        callback_data=f"pause|{m.from_user.id}"
                        if spotify_json["is_playing"]
                        else f"play|{m.from_user.id}",
                    ),
                    InlineKeyboardButton(
                        text="⏭", callback_data=f"next|{m.from_user.id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("play_in_sp"),
                        callback_data=f'tcs|{spotify_json["item"]["id"]}',
                    ),
                    InlineKeyboardButton(
                        text=t("search_lyric"),
                        callback_data=f'sp_s|{spotify_json["item"]["id"]}|{m.from_user.id}',
                    ),
                ],
            ]
        )

        if "artists" in spotify_json["item"]:
            publi = spotify_json["item"]["artists"][0]["name"]
        else:
            publi = spotify_json["item"]["show"]["name"]
        spotify_json = sess.current_playback(additional_types="episode,track")
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(
                f"🎵 {publi} - {spotify_json['item']['name']}",
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
        else:
            await m.answer(f"🎵 {publi} - {spotify_json['item']['name']}")
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(pause|play)"))
@use_chat_lang()
async def ppa(c: Client, m: CallbackQuery, t):
    cmd, user = m.data.split("|")
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        for i in devices["devices"]:
            if i["is_active"]:
                device_id = i["id"]
                break
        if "pause" in cmd:
            sess.pause_playback(device_id)
        else:
            sess.start_playback(device_id)
        spotify_json = sess.current_playback(additional_types="episode,track")
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⏮", callback_data=f"previous|{m.from_user.id}"
                    ),
                    InlineKeyboardButton(
                        text="⏸" if "play" in cmd else "▶️",
                        callback_data=f"pause|{m.from_user.id}"
                        if "play" in cmd
                        else f"play|{m.from_user.id}",
                    ),
                    InlineKeyboardButton(
                        text="⏭", callback_data=f"next|{m.from_user.id}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=t("play_in_sp"),
                        callback_data=f'tcs|{spotify_json["item"]["id"]}',
                    ),
                    InlineKeyboardButton(
                        text=t("search_lyric"),
                        callback_data=f'sp_s|{spotify_json["item"]["id"]}|{m.from_user.id}',
                    ),
                ],
            ]
        )

        if "artists" in spotify_json["item"]:
            publi = spotify_json["item"]["artists"][0]["name"]
        else:
            publi = spotify_json["item"]["show"]["name"]
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(
                f"🎵 {publi} - {spotify_json['item']['name']}",
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
        else:
            await m.edit_message_reply_markup(reply_markup=kb)
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
