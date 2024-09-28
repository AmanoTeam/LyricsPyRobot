import re
from datetime import datetime
from functools import partial

from hydrogram import Client, filters
from hydrogram.errors import ListenerTimeout
from hydrogram.helpers import ikb
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

import db
from config import login_url, sudos
from locales import default_language, get_locale_string, langdict, use_chat_lang
from utils import genius_client, get_spotify_session, musixmatch_client

# + original, - traduzido, _ telegraph


def generate_language_keyboard():
    languages = list(langdict)
    keyboard = []
    while languages:
        language = langdict[languages[0]]["main"]
        button_row = [
            InlineKeyboardButton(
                f"{language['language_flag']} {language['language_name']}",
                callback_data=f"set_lang {languages[0]}",
            )
        ]
        languages.pop(0)
        if languages:
            language = langdict[languages[0]]["main"]
            button_row.append(
                InlineKeyboardButton(
                    f"{language['language_flag']} {language['language_name']}",
                    callback_data=f"set_lang {languages[0]}",
                )
            )
            languages.pop(0)
        keyboard.append(button_row)
    return keyboard


@Client.on_callback_query(filters.regex(r"^(_\+)"))
@use_chat_lang()
async def teor(c: Client, m: CallbackQuery, t):
    user_id, hash_value = m.data[2:].split("|")
    if m.from_user.id != int(user_id) and m.from_user.id not in sudos:
        chat = await c.get_chat(int(user_id))
        await m.answer(t("not_allowed").format(first_name=chat.first_name))
        return

    url_data = db.get_url(hash_value)
    if not url_data:
        await m.answer(t("hash_nf"), show_alert=True)
        return

    if re.match(r"^(https?://)?(genius\.com/|(m\.|www\.)?genius\.com/).+", url_data[0]):
        lyrics_data = await genius_client.lyrics(hash_value)
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", url_data[0]
    ):
        lyrics_data = await musixmatch_client.lyrics(hash_value)
    else:
        await m.answer(t("url_nf").format(text=url_data[0]), show_alert=True)
        return

    parsed_lyrics = (
        genius_client.parse(lyrics_data)
        if "meta" in lyrics_data
        else musixmatch_client.parce(lyrics_data)
    )

    if musixmatch_client.translation(hash_value, "pt", None):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("text"), callback_data=f"+{user_id}|{hash_value}"
                    ),
                    InlineKeyboardButton(
                        text=t("port"), callback_data=f"_-{user_id}|{hash_value}"
                    ),
                ]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("text"), callback_data=f"+{user_id}|{hash_value}"
                    )
                ]
            ]
        )

    await m.edit_message_text(
        f'{parsed_lyrics["musica"]} - {parsed_lyrics["autor"]}\n{url_data[1]}',
        reply_markup=keyboard,
        parse_mode=None,
    )

    return


@Client.on_callback_query(filters.regex(r"^(_\-)"))
@use_chat_lang()
async def tetr(c: Client, m: CallbackQuery, t):
    user_id, hash_value = m.data[2:].split("|")
    if m.from_user.id != int(user_id) and m.from_user.id not in sudos:
        chat = await c.get_chat(int(user_id))
        await m.answer(t("not_allowed").format(first_name=chat.first_name))
        return

    url_data = db.get_url(hash_value)
    if not url_data:
        await m.answer(t("hash_nf"), show_alert=True)
        return

    if re.match(r"^(https?://)?(genius\.com/|(m\.|www\.)?genius\.com/).+", url_data[0]):
        lyrics_data = await genius_client.lyrics(hash_value)
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", url_data[0]
    ):
        lyrics_data = await musixmatch_client.lyrics(hash_value)
    else:
        await m.answer(t("url_nf").format(text=url_data[0]), show_alert=True)
        return

    parsed_lyrics = (
        genius_client.parse(lyrics_data)
        if "meta" in lyrics_data
        else musixmatch_client.parce(lyrics_data)
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("text"), callback_data=f"-{user_id}|{hash_value}"
                ),
                InlineKeyboardButton(
                    text=t("original"), callback_data=f"_+{user_id}|{hash_value}"
                ),
            ]
        ]
    )
    await m.edit_message_text(
        f'{parsed_lyrics["musica"]} - {parsed_lyrics["autor"]}\n{url_data[2]}',
        reply_markup=keyboard,
        parse_mode=None,
    )
    return


@Client.on_callback_query(filters.regex(r"^(\+)"))
@use_chat_lang()
async def ori(c: Client, m: CallbackQuery, t):
    user_id, hash_value = m.data[1:].split("|")
    if m.from_user.id != int(user_id) and m.from_user.id not in sudos:
        chat = await c.get_chat(int(user_id))
        await m.answer(t("not_allowed").format(first_name=chat.first_name))
        return

    url_data = db.get_url(hash_value)
    if not url_data:
        await m.answer(t("hash_nf"), show_alert=True)
        return

    if re.match(r"^(https?://)?(genius\.com/|(m\.|www\.)?genius\.com/).+", url_data[0]):
        lyrics_data = await genius_client.lyrics(hash_value)
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", url_data[0]
    ):
        lyrics_data = await musixmatch_client.lyrics(hash_value)
    else:
        await m.answer(t("url_nf").format(text=url_data[0]), show_alert=True)
        return

    parsed_lyrics = (
        genius_client.parse(lyrics_data)
        if "meta" in lyrics_data
        else musixmatch_client.parce(lyrics_data)
    )

    if musixmatch_client.translation(hash_value, "pt", None):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("tgph"),
                        callback_data=f"_+{user_id}|{hash_value}",
                    ),
                    InlineKeyboardButton(
                        text=t("port"), callback_data=f"-{user_id}|{hash_value}"
                    ),
                ]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("tgph"),
                        callback_data=f"_+{user_id}|{hash_value}",
                    )
                ]
            ]
        )

    await m.edit_message_text(
        f'[{parsed_lyrics["musica"]} - {parsed_lyrics["autor"]}]({parsed_lyrics["link"]})\n{parsed_lyrics["letra"]}'[
            :4096
        ],
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    return


@Client.on_callback_query(filters.regex(r"^(\-)"))
@use_chat_lang()
async def tr(c: Client, m: CallbackQuery, t):
    user_id, hash_value = m.data[1:].split("|")
    if m.from_user.id != int(user_id) and m.from_user.id not in sudos:
        chat = await c.get_chat(int(user_id))
        await m.answer(t("not_allowed").format(first_name=chat.first_name))
        return

    url_data = db.get_url(hash_value)
    if not url_data:
        await m.answer(t("hash_nf"), show_alert=True)
        return

    if re.match(r"^(https?://)?(genius\.com/|(m\.|www\.)?genius\.com/).+", url_data[0]):
        lyrics_data = await genius_client.lyrics(url_data[0])
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", url_data[0]
    ):
        lyrics_data = await musixmatch_client.lyrics(hash_value)
    else:
        await m.answer(t("url_nf").format(text=url_data[0]), show_alert=True)
        return

    parsed_lyrics = (
        genius_client.parse(lyrics_data)
        if "meta" in lyrics_data
        else musixmatch_client.parce(lyrics_data)
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("tgph"), callback_data=f"_-{user_id}|{hash_value}"
                ),
                InlineKeyboardButton(
                    text=t("original"), callback_data=f"+{user_id}|{hash_value}"
                ),
            ]
        ]
    )
    translated_lyrics = await musixmatch_client.translation(
        hash_value, "pt", parsed_lyrics["letra"]
    )
    await m.edit_message_text(
        f'[{parsed_lyrics["musica"]} - {parsed_lyrics["autor"]}]({parsed_lyrics["link"]})\n{translated_lyrics}'[
            :4096
        ],
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    return


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
                InlineKeyboardButton(
                    text="Spotify / Last.fm", callback_data="player_st"
                ),
                InlineKeyboardButton(text=t("np_apv"), callback_data="np_apv_pg0"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="start_back")],
        ]
    )
    await m.edit_message_text(t("settings_txt"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"player_st"))
@use_chat_lang()
async def player_settings(c: Client, m: CallbackQuery, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("spotify"), callback_data="spotify_st"),
                InlineKeyboardButton(text=t("lastfm"), callback_data="lastfm_st"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    await m.edit_message_text(t("player_st_txt"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"np_apv_pg"))
@use_chat_lang()
async def now_playing_approvals(c: Client, m: CallbackQuery, t):
    page = m.data.split("pg")[1]
    approved_ids = db.get_all_aproved(m.from_user.id)
    table = []
    row = []
    for i, id_data in enumerate(approved_ids):
        if i % 3 == 0 and i != 0:
            table.append(row)
            row = []
        user = await c.get_chat(id_data[1])
        if id_data[2] == 1:
            emoji = "✅"
        elif id_data[2] == 0:
            emoji = "❓"
        else:
            emoji = "❌"
        row.append((user.first_name + emoji, f"np_apvu_{id_data[1]}_pg{page}"))
    table.append(row)

    paginated_table = [table[i : i + 3] for i in range(0, len(table), 3)]
    extra_buttons = []

    if int(page) != 0:
        extra_buttons.append(("back", f"np_apv_pg{int(page) - 1}"))

    extra_buttons.append(("close", "settings"))

    if len(paginated_table) - int(page) > 1:
        extra_buttons.append(("next", f"np_apv_pg{int(page) + 1}"))

    keyboard = paginated_table[int(page)]
    keyboard.append(extra_buttons)

    await m.edit_message_text(t("np_apv_txt"), reply_markup=ikb(keyboard))


@Client.on_callback_query(filters.regex(r"np_apvu"))
@use_chat_lang()
async def now_playing_approval_user(c: Client, m: CallbackQuery, t):
    user_id, page = m.data.split("_")[2:]
    page = page.split("pg")[1]
    approval = db.get_aproved(m.from_user.id, user_id)
    user = await c.get_chat(user_id)
    text = t("apuser").format(
        name=f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    )
    keyboard = []
    if approval:
        if approval[0] == 1:
            date1 = (
                datetime.fromtimestamp(approval[2]).strftime("%d/%m/%Y %H:%M:%S")
                if approval[2]
                else "Nunca utilizado"
            )
            date2 = (
                datetime.fromtimestamp(approval[3]).strftime("%d/%m/%Y %H:%M:%S")
                if approval[3]
                else "Sem data"
            )
            text += t("apuser_txt").format(
                data=date2,
                data2=date1,
                count=approval[1] or "0",
            )
            keyboard.append([(t("block"), f"np_apvt_{user_id}_pg{page}")])
        elif approval[0] == 0:
            date = (
                datetime.fromtimestamp(approval[3]).strftime("%d/%m/%Y %H:%M:%S")
                if approval[3]
                else "Sem data"
            )
            text += f"Solicitado em: {date}"
            keyboard.append([(t("aprove"), f"np_apvt_{user_id}_pg{page}")])
        elif approval[0] == 2:
            date = (
                datetime.fromtimestamp(approval[3]).strftime("%d/%m/%Y %H:%M:%S")
                if approval[3]
                else "Sem data"
            )
            text += f"Reprovado em: {date}"
            keyboard.append([(t("unblock"), f"np_apvt_{user_id}_pg{page}")])

    keyboard.append([(t("back"), f"np_apv_pg{page}")])

    await m.edit_message_text(text, reply_markup=ikb(keyboard))


@Client.on_callback_query(filters.regex(r"np_apvt"))
@use_chat_lang()
async def now_playing_approval_toggle(c: Client, m: CallbackQuery, t):
    user_id, page = m.data.split("_")[2:]
    page = page.split("pg")[1]
    if approval := db.get_aproved(m.from_user.id, user_id):
        approval_status = "1" if approval[0] in {0, 2} else "2"
        db.add_aproved(
            m.from_user.id,
            user_id,
            approval_status,
            dates=datetime.now().timestamp(),
            usages=0,
        )
        m.data = f"np_apvu_{user_id}_pg{page}"
        await now_playing_approval_user(c, m)


@Client.on_callback_query(filters.regex(r"language"))
@use_chat_lang()
async def language(c: Client, m: CallbackQuery, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *generate_language_keyboard(),
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    await m.edit_message_text(t("ch_lang"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"theme|pattern"))
@use_chat_lang()
async def theme(c: Client, m: CallbackQuery, t):
    user_theme = db.theme(m.from_user.id)
    if user_theme[0] is None or ("_" in m.data and user_theme[0]):
        theme_id = 0
    elif "_" in m.data:
        theme_id = 1
    else:
        theme_id = user_theme[0]
    if user_theme[1] is None or ("-" in m.data and not user_theme[1]):
        blur_id = 1
    elif "-" in m.data:
        blur_id = 0
    else:
        blur_id = user_theme[1]
    if user_theme[2] is None or ("=" in m.data and user_theme[2]):
        pattern_id = False
    elif "=" in m.data:
        pattern_id = True
    else:
        pattern_id = user_theme[2]
    if user_theme[3] is None or ("+" in m.data and not user_theme[3]):
        sticker_id = 1
    elif "+" in m.data:
        sticker_id = 0
    else:
        sticker_id = user_theme[3]
    theme_names = [t("light"), t("dark")]
    blur_names = ["☑️", "✅"]
    pattern_names = [t("text"), t("tgph")]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("sticker"), callback_data="none"),
                InlineKeyboardButton(
                    text=blur_names[sticker_id], callback_data="theme+"
                ),
            ],
            [
                InlineKeyboardButton(text=t("theme"), callback_data="none"),
                InlineKeyboardButton(
                    text=theme_names[theme_id], callback_data="theme_"
                ),
            ],
            [
                InlineKeyboardButton(text=t("blur"), callback_data="none"),
                InlineKeyboardButton(text=blur_names[blur_id], callback_data="theme-"),
            ],
            [
                InlineKeyboardButton(text=t("pattern"), callback_data="none"),
                InlineKeyboardButton(
                    text=pattern_names[pattern_id], callback_data="theme="
                ),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="settings")],
        ]
    )
    db.def_theme(m.from_user.id, theme_id, blur_id, pattern_id, sticker_id)
    await m.edit_message_text(t("np_settings_txt"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"lastfm_st"))
@use_chat_lang()
async def lastfm_settings(c: Client, m: CallbackQuery, t):
    text = t("lastfm") + "\n\n"

    user_token = db.get(m.from_user.id)
    if not user_token or not user_token[2]:
        text += t("nologged_lfm")
    else:
        text += t("logged_lfm").format(name=user_token[2])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("login"), callback_data="lfm_login"),
                InlineKeyboardButton(text=t("logout"), callback_data="lfm_logout"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="player_st")],
        ]
    )

    await m.edit_message_text(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"lfm_login"))
@use_chat_lang()
async def lastfm_login(c: Client, m: CallbackQuery, t):
    await m.edit_message_text(t("lfm_login"))

    user_message = None

    while not user_message:
        try:
            user_message = await m.message.chat.listen(filters.text)
        except ListenerTimeout:
            return

    db.add_user_last(m.from_user.id, user_message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="lastfm_st")],
        ]
    )
    await m.edit_message_text(
        t("lfm_login_done").format(name=user_message.text), reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"lfm_logout"))
@use_chat_lang()
async def lastfm_logout(c: Client, m: CallbackQuery, t):
    db.add_user_last(m.from_user.id, None)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="lastfm_st")],
        ]
    )
    await m.edit_message_text(t("lfm_logout"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"spotify_st"))
@use_chat_lang()
async def spotify_settings(c: Client, m: CallbackQuery, t):
    text = t("spotify") + "\n\n"

    user_token = db.get(m.from_user.id)
    if not user_token or not user_token[0]:
        text += t("nologged")
    else:
        spotify_session = await get_spotify_session(m.from_user.id)
        profile = spotify_session.current_user()
        text += t("logged").format(name=profile["display_name"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("login"), web_app=WebAppInfo(url=login_url)
                ),
                InlineKeyboardButton(text=t("logout"), callback_data="sp_logout"),
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="player_st")],
        ]
    )

    await m.edit_message_text(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"sp_logout"))
@use_chat_lang()
async def spotify_logout(c: Client, m: CallbackQuery, t):
    db.add_user(m.from_user.id, None, None)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("back"), callback_data="spotify_st")],
        ]
    )
    await m.edit_message_text(t("sp_logout"), reply_markup=keyboard)


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
