from db import db, dbc

from pyromod.helpers import ikb
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

def get_user(user):
    dbc.execute(
        "SELECT test FROM users WHERE user_id = (?)", (user,)
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
            "INSERT INTO users (user_id, test) VALUES (?,?)", (user, t)
        )
    db.commit()

@Client.on_message(filters.command("start"))
async def start(c: Client, m: Message):
    if not get_user(m.from_user.id):
        set_user(m.from_user.id, 0)
    keyb = [
        [
            ("Config", "config")
        ]
    ]
    await m.reply("Hello", reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex(r"config"))
async def settings(c: Client, q: CallbackQuery):
    toggle = None
    if "_" in q.data:
        toggle = q.data.split("_")[1]
    if toggle == "t":
        set_user(q.from_user.id, 0 if get_user(q.from_user.id)[0] else 1)
    keyb = [
        [
            ("Test", "none"),
            (get_user(q.from_user.id)[0], "config_t")
        ]
    ]
    await q.edit_message_text("Configs: ", reply_markup=ikb(keyb))
