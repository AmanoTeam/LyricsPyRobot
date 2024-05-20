import re
from datetime import datetime
from functools import partial

from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ListenerTimeout

import db
from config import login_url, sudos
from locales import default_language, get_locale_string, langdict, use_chat_lang
from utils import get_spoti_session, letras, musixmatch

# + original, - traduzido, _ telegraph


def gen_langs_kb():
    langs = list(langdict)
    kb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [
            InlineKeyboardButton(
                f"{lang['language_flag']} {lang['language_name']}",
                callback_data=f"set_lang {langs[0]}",
            )
        ]
        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append(
                InlineKeyboardButton(
                    f"{lang['language_flag']} {lang['language_name']}",
                    callback_data=f"set_lang {langs[0]}",
                )
            )
            langs.pop(0)
        kb.append(a)
    return kb


@Client.on_callback_query(filters.regex(r"^(_\+)"))
@use_chat_lang()
async def teor(c: Client, m: CallbackQuery, t):
    user, hash = m.data[2:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
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
            a = letras.parce(a) if "art" in a else musixmatch.parce(a)
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
                f'{a["musica"]} - {a["autor"]}\n{n[1]}',
                reply_markup=keyboard,
                parse_mode=None,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(_\-)"))
@use_chat_lang()
async def tetr(c: Client, m: CallbackQuery, t):
    user, hash = m.data[2:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
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
            a = letras.parce(a) if "art" in a else musixmatch.parce(a)
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
                f'{a["musica"]} - {a["autor"]}\n{n[2]}',
                reply_markup=keyboard,
                parse_mode=None,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(\+)"))
@use_chat_lang()
async def ori(c: Client, m: CallbackQuery, t):
    user, hash = m.data[1:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
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
            a = letras.parce(a) if "art" in a else musixmatch.parce(a)
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
                f'[{a["musica"]} - {a["autor"]}]({a["link"]})\n{a["letra"]}'[:4096],
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"^(\-)"))
@use_chat_lang()
async def tr(c: Client, m: CallbackQuery, t):
    user, hash = m.data[1:].split("|")
    if m.from_user.id == int(user) or m.from_user.id in sudos:
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
            a = letras.parce(a) if "art" in a else musixmatch.parce(a)
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
            await m.edit_message_text(
                f'[{a["musica"]} - {a["autor"]}]({a["link"]})\n{trad}'[:4096],
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
    else:
        a = await c.get_chat(int(user))
        await m.answer(t("not_allowed").format(first_name=a.first_name))


@Client.on_callback_query(filters.regex(r"settings"))
@use_chat_lang()
async def settings(c: Client, m: CallbackQuery, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("np_settings"), callback_data="theme"),
                InlineKeyboardButton(text=t("language"), callback_data="language"),
            ],
            [
                InlineKeyboardButton(text="Spotify / Last.fm", callback_data="player_st"),
                InlineKeyboardButton(text=t("np_apv"), callback_data="np_apv_pg0"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="start_back")],
        ]
    )
    await m.edit_message_text(t("settings_txt"), reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"player_st"))
@use_chat_lang()
async def player_st(c: Client, m: CallbackQuery, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("spotify"), callback_data="spotify_st"),
             InlineKeyboardButton(text=t("lastfm"), callback_data="lastfm_st")],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    await m.edit_message_text(t("player_st_txt"), reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"np_apv_pg"))
@use_chat_lang()
async def np_apv(c: Client, m: CallbackQuery, t):
    pg = m.data.split("pg")[1]
    ids = db.get_all_aproved(m.from_user.id)
    table = []
    row = []
    for i, id in enumerate(ids):
        if i % 3 == 0 and i != 0:
            table.append(row)
            row = []
        usr = await c.get_chat(id[1])
        if id[2] == 1:
            emoji = "✅"
        elif id[2] == 0:
            emoji = "❓"
        else:
            emoji = "❌"
        row.append((usr.first_name + emoji, f"np_apvu_{id[1]}_pg{pg}"))
    table.append(row)

    tabela = [table[i : i + 3] for i in range(0, len(table), 3)]
    extra = []

    if int(pg) != 0:
        extra.append(("back", f"np_apv_pg{int(pg)-1}"))

    extra.append(("close", "settings"))

    if len(tabela) - int(pg) > 1:
        extra.append(("next", f"np_apv_pg{int(pg)+1}"))

    keyb = tabela[int(pg)]
    keyb.append(extra)

    await m.edit_message_text(t("np_apv_txt"), reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex(r"np_apvu"))
@use_chat_lang()
async def np_apvu(c: Client, m: CallbackQuery, t):
    id, pg = m.data.split("_")[2:]
    pg = pg.split("pg")[1]
    app = db.get_aproved(m.from_user.id, id)
    usr = await c.get_chat(id)
    text = t("apuser").format(
        name=f"<a href='tg://user?id={usr.id}'>{usr.first_name}</a>"
    )
    keyb = []
    if app:
        if app[0] == 1:
            date1 = (
                datetime.fromtimestamp(app[2]).strftime("%d/%m/%Y %H:%M:%S")
                if app[2]
                else "Nunca utilizado"
            )
            date2 = (
                datetime.fromtimestamp(app[3]).strftime("%d/%m/%Y %H:%M:%S")
                if app[3]
                else "Sem data"
            )
            text += t("apuser_txt").format(
                data=date2,
                data2=date1,
                count=app[1] or "0",
            )
            keyb.append([(t("block"), f"np_apvt_{id}_pg{pg}")])
        elif app[0] == 0:
            date = (
                datetime.fromtimestamp(app[3]).strftime("%d/%m/%Y %H:%M:%S")
                if app[3]
                else "Sem data"
            )
            text += "Solicitado em: {data}".format(
                data=date
            )
            keyb.append([(t("aprove"), f"np_apvt_{id}_pg{pg}")])
        elif app[0] == 2:
            date = (
                datetime.fromtimestamp(app[3]).strftime("%d/%m/%Y %H:%M:%S")
                if app[3]
                else "Sem data"
            )
            text += "Reprovado em: {data}".format(
                data=date
            )
            keyb.append([(t("unblock"), f"np_apvt_{id}_pg{pg}")])

    keyb.append([(t("back"), f"np_apv_pg{pg}")])

    await m.edit_message_text(text, reply_markup=ikb(keyb))


@Client.on_callback_query(filters.regex(r"np_apvt"))
@use_chat_lang()
async def np_apvt(c: Client, m: CallbackQuery, t):
    id, pg = m.data.split("_")[2:]
    pg = pg.split("pg")[1]
    app = db.get_aproved(m.from_user.id, id)
    if app:
        appv = "1" if app[0] in [0, 2] else "2"
        db.add_aproved(
            m.from_user.id, id, appv, dates=datetime.now().timestamp(), usages=0
        )
        m.data = f"np_apvu_{id}_pg{pg}"
        await np_apvu(c, m)


@Client.on_callback_query(filters.regex(r"language"))
@use_chat_lang()
async def lang(c: Client, m: CallbackQuery, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_langs_kb(),
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    await m.edit_message_text(t("ch_lang"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"theme|pattern"))
@use_chat_lang()
async def theme(c: Client, m: CallbackQuery, t):
    a = db.theme(m.from_user.id)
    if a[0] is None or "_" in m.data and a[0]:
        tid = 0
    elif "_" in m.data:
        tid = 1
    else:
        tid = a[0]
    if a[1] is None or "-" in m.data and not a[1]:
        bid = 1
    elif "-" in m.data:
        bid = 0
    else:
        bid = a[1]
    if a[2] is None or "=" in m.data and a[2]:
        pid = False
    elif "=" in m.data:
        pid = True
    else:
        pid = a[2]
    if a[3] is None or "+" in m.data and not a[3]:
        sid = 1
    elif "+" in m.data:
        sid = 0
    else:
        sid = a[3]
    tname = [t("light"), t("dark")]
    bname = ["☑️", "✅"]
    pname = [t("text"), t("tgph")]
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
            [
                InlineKeyboardButton(text=t("pattern"), callback_data="none"),
                InlineKeyboardButton(text=pname[pid], callback_data="theme="),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    db.def_theme(m.from_user.id, tid, bid, pid, sid)
    await m.edit_message_text(t("np_settings_txt"), reply_markup=keyboard)

@Client.on_callback_query(filters.regex(r"lastfm_st"))
@use_chat_lang()
async def lastfm_st(c: Client, m: CallbackQuery, t):
    text = t("lastfm") + "\n\n"

    tk = db.get(m.from_user.id)
    if not tk or not tk[2]:
        text += t("nologged_lfm")
    else:
        text += t("logged_lfm").format(name=tk[2])

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("login"), callback_data="lfm_login"),
             InlineKeyboardButton(text=t("logout"), callback_data="lfm_logout")],
            [InlineKeyboardButton(text=t("back"), callback_data="player_st")],
        ]
    )

    await m.edit_message_text(text, reply_markup=kb)

@Client.on_callback_query(filters.regex(r"lfm_login"))
@use_chat_lang()
async def lfm_login(c: Client, m: CallbackQuery, t):
    await m.edit_message_text(t("lfm_login"))

    cmessage = None

    while not cmessage:
        try:
            cmessage = await m.message.chat.listen(filters.text)
        except ListenerTimeout:
            return

    db.add_user_last(m.from_user.id, cmessage.text)

    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="lastfm_st")],
        ]
    )
    await m.edit_message_text(t("lfm_login_done").format(name=cmessage.text), reply_markup=keyb)

@Client.on_callback_query(filters.regex(r"lfm_logout"))
@use_chat_lang()
async def lfm_logout(c: Client, m: CallbackQuery, t):
    db.add_user_last(m.from_user.id, None)
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="lastfm_st")],
        ]
    )
    await m.edit_message_text(t("lfm_logout"), reply_markup=keyb)

@Client.on_callback_query(filters.regex(r"spotify_st"))
@use_chat_lang()
async def spotify_st(c: Client, m: CallbackQuery, t):
    text = t("spotify") + "\n\n"

    tk = db.get(m.from_user.id)
    if not tk or not tk[0]:
        text += t("nologged")
    else:
        sp = await get_spoti_session(m.from_user.id)
        profile = sp.current_user()
        text += t("logged").format(name=profile["display_name"])

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("login"), url=login_url),
             InlineKeyboardButton(text=t("logout"), callback_data="sp_logout")],
            [InlineKeyboardButton(text=t("back"), callback_data="player_st")],
        ]
    )

    await m.edit_message_text(text, reply_markup=kb)

@Client.on_callback_query(filters.regex(r"sp_logout"))
@use_chat_lang()
async def sp_logout(c: Client, m: CallbackQuery, t):
    db.add_user(m.from_user.id, None, None)
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="spotify_st")],
        ]
    )
    await m.edit_message_text(t("sp_logout"), reply_markup=keyb)


@Client.on_callback_query(filters.regex("^set_lang "))
@use_chat_lang()
async def set_user_lang(c: Client, m: CallbackQuery, f):
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
