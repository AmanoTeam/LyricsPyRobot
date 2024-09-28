import re

from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import db
from locales import use_chat_lang
from utils import genius, musixmatch

# + original, - traduzido, _ telegraph


@Client.on_message(filters.command(["lyrics", "letra"]))
@use_chat_lang()
async def letra(c: Client, m: Message, t):
    print(m)
    text = m.text.split(" ", 1)[1]
    if not text:
        await m.reply_text(t("use"))
    elif "spotify:" in text:
        a = await musixmatch.auto(id=text.split(":", 1)[1])
    elif re.match(
        r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", text
    ):
        a = await genius.auto(text)
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", text
    ):
        a = await musixmatch.lyrics(text)
    else:
        try:
            a = await musixmatch.auto(text, limit=1, lang="pt") or await genius.auto(
                text, limit=1
            )
        except Exception:
            a = await genius.auto(text, limit=1)
        if not a:
            await m.reply_text(t("lyrics_nf"))
            return
    a = a[0] if isinstance(a, list) else a
    print(a)
    a = genius.parse(a) if "meta" in a else musixmatch.parce(a)
    print(a)
    hash = str(a["id"])
    db.add_hash(hash, a)
    uid = m.from_user.id
    if ma := db.theme(m.from_user.id)[2]:
        if a["traducao"]:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{uid}|{hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"_-{uid}|{hash}"
                        ),
                    ]
                ]
            )
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{uid}|{hash}"
                        )
                    ]
                ]
            )
        await m.reply_text(
            f'{a["musica"]} - {a["autor"]}\n{db.get_url(hash)[1]}',
            reply_markup=keyboard,
            parse_mode=None,
        )
    else:
        keyboard = (
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{uid}|{hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"-{uid}|{hash}"
                        ),
                    ]
                ]
            )
            if a["traducao"]
            else InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{uid}|{hash}"
                        )
                    ]
                ]
            )
        )
        await m.reply_text(
            f"[{a['musica']} - {a['autor']}]({a['link']})\n{a['letra']}"[:4096],
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    return
