import spotipy
from db import dbc, db
from lyricspy.aio import Musixmatch
from config import MUSIXMATCH_CONFIG

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from locales import use_chat_lang
from utils import get_spoti_session, gen_spotify_token, get_user

mux = Musixmatch(MUSIXMATCH_CONFIG)

login_url = ("https://accounts.spotify.com/authorize?response_type=code&"
            + "client_id=6fa50508cfdc4d1490ce8cf29d12097a&"
            + "scope=user-read-currently-playing+user-modify-playback-state+user-read-playback-state&"
            + "redirect_uri=https://lyricspy.amanoteam.com/go")

@Client.on_callback_query(filters.regex(r"^sp_config main"))
@use_chat_lang()
async def sp_config(c:Client, q:CallbackQuery, t):
    usr = get_user(q.from_user.id)
    text = t("title")
    if not usr:
        login_kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=t("login"),
                    url=login_url,
                )
            ]]
        )
        return await q.edit_message_text(t("not_logged"), reply_markup=login_kb)
    else:
        sp = await get_spoti_session(q.from_user.id)
        profile = sp.current_user()
        text += t("logged").format(name=profile["display_name"])
    
    await q.edit_message_text(text)

@Client.on_message(filters.command("spoti"))
@use_chat_lang()
async def spoti(c: Client, m: Message, t):
    tx = m.text.split(" ", 1)
    if len(tx) == 2:
        get = await gen_spotify_token(m.from_user.id, tx[1])
        if get[0]:
            sp = await get_spoti_session(m.from_user.id)
            profile = sp.current_user()
            await m.reply(t("login_done").format(name=profile["display_name"]))
        else:
            await m.reply(t("login_error").format(error=get[1]))
    else:
        usr = get_user(m.from_user.id)
        if not usr:
            login_kb = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=t("login"),
                        url=login_url,
                    )
                ]]
            )
            await m.reply(t("not_logged"), reply_markup=login_kb)

@Client.on_message(filters.command("np"))
@use_chat_lang()
async def start_np(c: Client, m: Message, t):
    await spotify_np(c, m)

async def spotify_np(c: Client, m: Message):
    usr = get_user(m.from_user.id)
    if usr:
        sp = await get_spoti_session(m.from_user.id)
        
        spotify_json = sp.current_user_playing_track()
        if not spotify_json:
            return False
        mtext = f"🎵 {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}"
        print(mtext)
        mjson = await mux.lyrics(artist=spotify_json['item']['artists'][0]['name'], track=spotify_json['item']['name'])
        a = mux.parce(mjson)
        await m.reply_text(
            f"[{a['musica']} - {a['autor']}]({a['link']})\n{a['letra']}"[:4096],
            reply_markup=None,
            disable_web_page_preview=True,
        )
        return True
    return False
