from hydrogram import Client
from hydrogram.types import (
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import db
from locales import use_chat_lang
from utils import musixmatch

# + original, - traduzido, _ telegraph


@Client.on_chosen_inline_result()
@use_chat_lang()
async def choosen(c: Client, m: ChosenInlineResult, t):
    if m.result_id == "MySpotify":
        return
    hash = m.result_id[1:] if m.result_id[0] in {"s", "l"} else m.result_id
    a = await musixmatch.lyrics(hash)
    a = musixmatch.parce(a)
    uid = m.from_user.id
    if ma := db.theme(uid)[2]:
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
        await c.edit_inline_text(
            m.inline_message_id,
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
        db.add_hash(hash, a)
        await c.edit_inline_text(
            m.inline_message_id,
            f"[{a['musica']} - {a['autor']}]({a['link']})\n{a['letra']}"[:4096],
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
