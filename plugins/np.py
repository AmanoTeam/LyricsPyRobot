import re
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import db
from locales import use_chat_lang, use_user_lang
from utils import (
    get_current,
    get_song_art,
    get_spoti_session,
    get_track_info,
    http_pool,
)

from utils import musixmatch
from .letra import letra

LFM_LINK_RE = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_message(filters.command("np"))
@use_chat_lang()
async def np(c: Client, m: Message, t):
    text = m.text.split(" ", 1)
    duid = m.from_user.id
    if len(text) == 2:
        usr = await c.get_chat(text[1])
        xm = db.get_aproved(usr.id, m.from_user.id)
        if usr.type != ChatType.PRIVATE:
            return await m.reply_text(t("only_users"))
        if usr.id == m.from_user.id or (xm and xm[0] == 1):
            usages = xm[1] + 1 if xm[1] else 1
            db.add_aproved(
                usr.id,
                m.from_user.id,
                xm[0],
                usages=usages,
                dates=datetime.now().timestamp(),
            )
            duid = m.from_user.id
            m.from_user.id = usr.id
        elif xm and xm[0] == 0:
            return await m.reply_text(
                t("not_aproved").format(first_name=usr.first_name)
            )
        elif xm and xm[0] == 2:
            return await m.reply_text(t("blocked").format(first_name=usr.first_name))
        else:
            ut = use_user_lang(usr.id)
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=ut("aprove"),
                            callback_data=f"aprova|{m.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text=ut("deny"),
                            callback_data=f"negar|{m.from_user.id}",
                        ),
                    ]
                ]
            )
            db.add_aproved(
                usr.id, m.from_user.id, False, dates=datetime.now().timestamp()
            )
            await c.send_message(
                usr.id,
                ut("aprrovedu").format(name=m.from_user.first_name),
                reply_markup=kb,
            )
            return await m.reply(t("approvedr").format(name=usr.first_name))
    try:
        sess = await get_spoti_session(m.from_user.id)
    except Exception:
        return await m.reply_text(t("not_logged"))
    if not sess or sess.current_playback() is None:
        tk = db.get(m.from_user.id)
        if not tk or not tk[2]:
            return await m.reply_text(t("not_logged"))
        a = await get_current(tk[2])
        if not a:
            return await m.reply_text(t("not_playing"))
        track_info = await get_track_info(tk[2], a[0]["artist"]["#text"], a[0]["name"])
        stick = db.theme(duid)[3]
        mtext = f"🎵 {a[0]['artist']['#text']} - {a[0]['name']}"
        if stick is not None and not stick:
            return await m.reply(
                mtext,
                parse_mode=ParseMode.HTML,
            )

        album_url = a[0]["image"][-1]["#text"]
        if not album_url:
            # if not present in api return, try to get album url from page
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
            color="dark" if db.theme(duid)[0] else "light",
            blur=db.theme(duid)[1],
            scrobbles=track_info["track"]["userplaycount"],
        )
        return await m.reply_document(album_art, caption=mtext)
    spotify_json = sess.current_playback(additional_types="episode,track")
    stick = db.theme(duid)[3]
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
            color="dark" if db.theme(duid)[0] else "light",
            blur=db.theme(duid)[1],
        )
    mtext = f"🎵 {publi} - {spotify_json['item']['name']}"
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
                InlineKeyboardButton(text="⏭", callback_data=f"next|{m.from_user.id}"),
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
        await m.reply_document(album_art, reply_markup=kb, caption=mtext)
    else:
        mtext = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
        mtext += f'🗣 {spotify_json["device"]["name"]} | ⏳{timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
        await m.reply(
            mtext,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
        )


@Client.on_callback_query(filters.regex(r"^aprova"))
@use_chat_lang()
async def aprova(c: Client, m: CallbackQuery, t):
    uid = m.data.split("|")[1]
    db.add_aproved(m.from_user.id, uid, True)
    usr = await c.get_users(uid)
    ut = use_user_lang(usr.id)
    await c.send_message(uid, ut("aproved").format(first_name=m.from_user.first_name))
    await m.edit_message_text(t("saproved").format(first_name=usr.first_name))


@Client.on_callback_query(filters.regex(r"^negar"))
@use_chat_lang()
async def negar(c: Client, m: CallbackQuery, t):
    uid = m.data.split("|")[1]
    db.add_aproved(m.from_user.id, uid, 2)
    usr = await c.get_users(uid)
    ut = use_user_lang(usr.id)
    await c.send_message(uid, ut("denied").format(first_name=m.from_user.first_name))
    await m.edit_message_text(t("sdenied").format(first_name=usr.first_name))


@Client.on_callback_query(filters.regex(r"^sp_s"))
async def sp_search(c: Client, m: CallbackQuery):
    track, uid = m.data.split("|")[1:]
    if m.from_user.id == int(uid):
        sess = await get_spoti_session(m.from_user.id)
        om = m.message
        om.from_user = m.from_user
        spotify_json = sess.track(track)
        a = await musixmatch.spotify_lyrics(artist=spotify_json['artists'][0]['name'], track=spotify_json['name'])
        if a:
            om.text = "/letra spotify:"+str(a['message']['body']['macro_calls']['matcher.track.get']['message']['body']['track']['track_id'])
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
            mtext = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
            mtext += f'🗣 {spotify_json["device"]["name"]} | ⏳{timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
            await m.edit_message_text(
                mtext,
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
            mtext = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
            mtext += f'🗣 {spotify_json["device"]["name"]} | ⏳{timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
            await m.edit_message_text(
                mtext,
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
            mtext = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
            mtext += f'🗣 {spotify_json["device"]["name"]} | ⏳{timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
            await m.edit_message_text(
                mtext,
                reply_markup=kb,
                parse_mode=ParseMode.HTML,
            )
        else:
            await m.edit_message_reply_markup(reply_markup=kb)
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))
