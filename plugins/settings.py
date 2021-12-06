from db import db, dbc
from functools import partial
from utils import gen_lang_keyboard

from pyromod.helpers import ikb
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from locales import use_chat_lang, default_language, langdict, db_set_lang, get_locale_string

def get_user(user):
    dbc.execute(
        "SELECT test, lang FROM users WHERE user_id = (?)", (user,)
    )
    try:
        return dbc.fetchone()
    except IndexError:
        return None

def set_user(user, t):
    if get_user(user):
        db.execute(
            "UPDATE users SET test = ? WHERE user_id = ?", (t, user)
        )
    else:
        db.execute(
            "INSERT INTO users (user_id, test, pro) VALUES (?,?, ?)", (user, t, 0)
        )
    db.commit()

@Client.on_callback_query(filters.regex(r"settings"))
@use_chat_lang()
async def config(c: Client, q: CallbackQuery, t):
    print("bot_used")
    keyb = [
        [
            ("Spotify settings", "sp_config")
        ],
        [
            ("Last.fm settings", "lm_config")
        ],
        [
            ("Another settings", "config")
        ]
    ]

    await q.edit_message_text(t("config_text"), reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex(r"config"))
@use_chat_lang()
async def settings(c: Client, q: CallbackQuery, t):
    if "_" in q.data:
        toggle = q.data.split("_")[1]
        if toggle == "t":
            set_user(q.from_user.id, 0 if get_user(q.from_user.id)[0] else 1)
    ulang = get_user(q.from_user.id)[1]
    if not ulang:
        ulang = default_language
    strings = partial(
        get_locale_string,
        langdict[ulang].get("main", langdict[default_language]["main"]),
        ulang,
        "main",
    )
    keyb = [
        [
            ("Test", "config_t"),
            (get_user(q.from_user.id)[0], "config_t")
        ],
        [
            (t("lang_c"), "lang_conf"),
            (strings("language_flag")+" "+strings("language_name"), "lang_conf")
        ],
        [
            (t("back"), "settings")
        ]
    ]
    await q.edit_message_text(t("config_text")+".", reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex(r"lang_conf"))
@use_chat_lang()
async def lang_conf(c: Client, q: CallbackQuery, t):
    keyb = [*gen_lang_keyboard(), [(t("back"), "config")]]
    await q.edit_message_text(t("select_lang"), reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex("^set_lang "))
async def set_user_lang(c, m):
    lang = m.data.split()[1]
    db_set_lang(m.from_user.id, lang)
    strings = partial(
        get_locale_string,
        langdict[lang].get("start", langdict[default_language]["start"]),
        lang,
        "start",
    )

    keyboard = [[(strings("back"), "config")]]
    await m.message.edit_text(strings("lang_sucess"), reply_markup=ikb(keyboard))
