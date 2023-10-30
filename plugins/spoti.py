from pyrogram import Client, filters
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import db
from config import login_url
from locales import use_chat_lang
from utils import get_song_art, get_spoti_session, get_token

from .letra import letra


@Client.on_message(filters.command("spoti"))
@use_chat_lang()
async def spoti(c: Client, m: Message, t):
    print("a")
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
            try:
                sess = await get_spoti_session(m.from_user.id)
            except:
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
            if not spotify_json:
                print("b")
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
                    await m.reply_document(album_art, caption=mtext)
                else:
                    await m.reply(
                        mtext,
                        parse_mode=ParseMode.HTML,
                    )
                m.text = f"/letra {spotify_json['item']['artists'][0]['name']} {spotify_json['item']['name']}"
                await letra(c, m)
