import re
from functools import partial

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import db
from config import sudos
from locales import default_language, get_locale_string, langdict, use_chat_lang
from utils import letras, musixmatch

# + original, - traduzido, _ telegraph


def gen_langs_kb():
    langs = list(langdict)
    kb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [
            InlineKeyboardButton(
                f"{lang['language_flag']} {lang['language_name']}",
                callback_data="set_lang " + langs[0],
            )
        ]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append(
                InlineKeyboardButton(
                    f"{lang['language_flag']} {lang['language_name']}",
                    callback_data="set_lang " + langs[0],
                )
            )
            langs.pop(0)
        kb.append(a)
    return kb


@Client.on_callback_query(filters.regex(r"^(_\+)"))
@use_chat_lang()
async def teor(c, m, t):
    user, hash = m.data[2:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        print(hash)
        n = db.get_url(hash)
        if not n:
            await m.answer(t("hash_nf"), show_alert=True)
        else:
            if re.match(
                r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", n[0]
            ):
                a = await letras.letra(n[0])
            elif re.match(
                r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", n[0]
            ):
                a = await musixmatch.lyrics(hash)
            else:
                await m.answer(t("url_nf").format(text=n[0]), show_alert=True)
                return True
            if "art" in a:
                a = letras.parce(a)
            else:
                a = musixmatch.parce(a)
            if musixmatch.translation(hash, "pt", None):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("text"), callback_data=f"+{user}|{hash}"
                            ),
                            InlineKeyboardButton(
                                text=t("port"), callback_data=f"_-{user}|{hash}"
                            ),
                        ]
                    ]
                )
            else:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("text"), callback_data=f"+{user}|{hash}"
                            )
                        ]
                    ]
                )
            await m.edit_message_text(
                "{} - {}\n{}".format(a["musica"], a["autor"], n[1]),
                reply_markup=keyboard,
                parse_mode=None,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(_\-)"))
@use_chat_lang()
async def tetr(c, m, t):
    user, hash = m.data[2:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        print(hash)
        if not n:
            await m.answer(t("hash_nf"), show_alert=True)
        else:
            if re.match(
                r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", n[0]
            ):
                a = await letras.letra(n[0])
            elif re.match(
                r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", n[0]
            ):
                a = await musixmatch.lyrics(hash)
            else:
                await m.answer(t("url_nf").format(text=n[0]), show_alert=True)
                return True
            if "art" in a:
                a = letras.parce(a)
            else:
                a = musixmatch.parce(a)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"-{user}|{hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("original"), callback_data=f"_+{user}|{hash}"
                        ),
                    ]
                ]
            )
            await m.edit_message_text(
                "{} - {}\n{}".format(a["musica"], a["autor"], n[2]),
                reply_markup=keyboard,
                parse_mode=None,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(\+)"))
@use_chat_lang()
async def ori(c, m, t):
    user, hash = m.data[1:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        print(hash)
        if not n:
            await m.answer(t("hash_nf"), show_alert=True)
        else:
            if re.match(
                r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", n[0]
            ):
                a = await letras.letra(n[0])
            elif re.match(
                r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", n[0]
            ):
                a = await musixmatch.lyrics(hash)
            else:
                await m.answer(t("url_nf").format(text=n[0]), show_alert=True)
                return True
            if "art" in a:
                a = letras.parce(a)
            else:
                a = musixmatch.parce(a)
            if musixmatch.translation(hash, "pt", None):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("tgph"), callback_data=f"_+{user}|{hash}"
                            ),
                            InlineKeyboardButton(
                                text=t("port"), callback_data=f"-{user}|{hash}"
                            ),
                        ]
                    ]
                )
            else:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("tgph"), callback_data=f"_+{user}|{hash}"
                            )
                        ]
                    ]
                )
            await m.edit_message_text(
                "[{} - {}]({})\n{}".format(
                    a["musica"], a["autor"], a["link"], a["letra"]
                )[:4096],
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(\-)"))
@use_chat_lang()
async def tr(c, m, t):
    user, hash = m.data[1:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        print(hash)
        if not n:
            await m.answer(t("hash_nf"), show_alert=True)
        else:
            if re.match(
                r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", n[0]
            ):
                a = await letras.letra(n[0])
            elif re.match(
                r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", n[0]
            ):
                a = await musixmatch.lyrics(hash)
            else:
                await m.answer(t("url_nf").format(text=n[0]), show_alert=True)
                return True
            if "art" in a:
                a = letras.parce(a)
            else:
                a = musixmatch.parce(a)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_-{user}|{hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("original"), callback_data=f"+{user}|{hash}"
                        ),
                    ]
                ]
            )
            trad = await musixmatch.translation(hash, "pt", a["letra"])
            print(trad)
            await m.edit_message_text(
                "[{} - {}]({})\n{}".format(
                    a["musica"], a["autor"], a["link"], trad
                )[:4096],
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"settings"))
@use_chat_lang()
async def settings(c, m, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("np_settings"), callback_data="theme")],
            [InlineKeyboardButton(text=t("language"), callback_data="language")],
            [InlineKeyboardButton(text=t("pattern"), callback_data="pattern")],
        ]
    )
    await m.edit_message_text(t("settings_txt"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"language"))
@use_chat_lang()
async def lang(c, m, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_langs_kb(),
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    await m.edit_message_text(t("ch_lang"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"theme"))
@use_chat_lang()
async def theme(c, m, t):
    a = db.theme(m.from_user.id)
    if a[0] is None or "_" in m.data and a[0]:
        tid = 0
    elif "_" in m.data and not a[0]:
        tid = 1
    else:
        tid = a[0]
    if a[1] is None or "-" in m.data and not a[1]:
        bid = 1
    elif "-" in m.data and a[1]:
        bid = 0
    else:
        bid = a[1]
    if a[3] is None or "+" in m.data and not a[3]:
        sid = 1
    elif "+" in m.data and a[1]:
        sid = 0
    else:
        sid = a[3]
    tname = [t("light"), t("dark")]
    bname = ["☑️", "✅"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("sticker"), callback_data="none"),
                InlineKeyboardButton(text=bname[sid], callback_data="theme+"),
            ],
            [
                InlineKeyboardButton(text=t("theme"), callback_data="none"),
                InlineKeyboardButton(text=tname[tid], callback_data="theme_"),
            ],
            [
                InlineKeyboardButton(text=t("blur"), callback_data="none"),
                InlineKeyboardButton(text=bname[bid], callback_data="theme-"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    db.def_theme(m.from_user.id, tid, bid, a[2], sid)
    await m.edit_message_text(t("np_settings_txt"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"pattern"))
@use_chat_lang()
async def pattern(c, m, t):
    a = db.theme(m.from_user.id)
    if a[2] is None or "_" in m.data and a[2]:
        pid = False
    elif "_" in m.data and not a[2]:
        pid = True
    else:
        pid = a[2]
    pname = [t("text"), t("tgph")]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=pname[pid], callback_data="pattern_")],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    db.def_theme(m.from_user.id, a[0], a[1], pid, a[3])
    await m.edit_message_text(t("pattern_settings_text"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^set_lang "))
@use_chat_lang()
async def set_user_lang(c, m, f):
    lang = m.data.split()[1]
    db.db_set_lang(m.from_user.id, lang)
    strings = partial(
        get_locale_string,
        langdict[lang].get("callback", langdict[default_language]["callback"]),
        lang,
        "callback",
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(strings("back"), callback_data="settings")]
        ]
    )
    await m.message.edit_text(strings("lang_sucess"), reply_markup=keyboard)
