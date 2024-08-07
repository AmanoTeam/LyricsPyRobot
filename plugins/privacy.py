from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from db import db, dbc
from locales import use_chat_lang


@Client.on_message(filters.command("privacy"))
@Client.on_callback_query(filters.regex(r"^privacy$"))
@use_chat_lang()
async def privacy(c: Client, m: Message | CallbackQuery, t):
    if isinstance(m, CallbackQuery):
        chat = m.message.chat
        func = m.edit_message_text
    else:
        chat = m.chat
        func = m.reply
    kb = [[(t("delete_data"), "delete_data")]]
    await func(
        t("privacy"),
        reply_markup=ikb(kb) if chat.type == ChatType.PRIVATE else None,
    )


@Client.on_callback_query(filters.regex(r"^delete_data$"))
@use_chat_lang()
async def delete_data(c: Client, q: CallbackQuery, t):
    kb = [[(t("yes"), "delete_data_confirm"), (t("no"), "delete_data_cancel")]]
    await q.edit_message_text(t("confirm_delete_data"), reply_markup=ikb(kb))


@Client.on_callback_query(filters.regex(r"^delete_data_confirm$"))
@use_chat_lang()
async def delete_data_confirm(c: Client, q: CallbackQuery, t):
    dbc.execute("DELETE FROM users WHERE user_id = ?", (q.from_user.id,))
    dbc.execute(
        "DELETE FROM aproved WHERE user_id = ? OR user = ?",
        (
            q.from_user.id,
            q.from_user.id,
        ),
    )
    db.commit()
    await q.edit_message_text(t("data_deleted"))


@Client.on_callback_query(filters.regex(r"^delete_data_cancel$"))
@use_chat_lang()
async def delete_data_cancel(c: Client, q: CallbackQuery, t):
    kb = [[(t("back"), "privacy")]]
    await q.edit_message_text(t("data_not_deleted"), reply_markup=ikb(kb))
