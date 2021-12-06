from db import db, dbc

from pyromod.helpers import ikb
from pyrogram import Client, filters
from pyrogram.types import Message
from locales import use_chat_lang

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

@Client.on_message(filters.command("start"))
@use_chat_lang()
async def start(c: Client, m: Message, t):
    if not get_user(m.from_user.id):
        set_user(m.from_user.id, 0)
    keyb = [
        [
            (t("config"), "settings"),
            (t("donate"), "donate")
        ]
    ]
    await m.reply(t("start"), reply_markup=ikb(keyb))
