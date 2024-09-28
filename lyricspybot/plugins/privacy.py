from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from lyricspybot.database import database, database_cursor
from lyricspybot.locales import use_chat_lang


@Client.on_message(filters.command("privacy"))
@Client.on_callback_query(filters.regex(r"^privacy$"))
@use_chat_lang()
async def privacy(c: Client, m: Message | CallbackQuery, t):
    if isinstance(m, CallbackQuery):
        current_chat = m.message.chat
        response_function = m.edit_message_text
    else:
        current_chat = m.chat
        response_function = m.reply
    keyboard_buttons = [[(t("delete_data"), "delete_data")]]
    await response_function(
        t("privacy"),
        reply_markup=ikb(keyboard_buttons)
        if current_chat.type == ChatType.PRIVATE
        else None,
    )


@Client.on_callback_query(filters.regex(r"^delete_data$"))
@use_chat_lang()
async def delete_data(c: Client, query: CallbackQuery, t):
    keyboard_buttons = [
        [(t("yes"), "delete_data_confirm"), (t("no"), "delete_data_cancel")]
    ]
    await query.edit_message_text(
        t("confirm_delete_data"), reply_markup=ikb(keyboard_buttons)
    )


@Client.on_callback_query(filters.regex(r"^delete_data_confirm$"))
@use_chat_lang()
async def delete_data_confirm(c: Client, query: CallbackQuery, t):
    database_cursor.execute(
        "DELETE FROM users WHERE user_id = ?", (query.from_user.id,)
    )
    database_cursor.execute(
        "DELETE FROM approved WHERE user_id = ? OR user = ?",
        (
            query.from_user.id,
            query.from_user.id,
        ),
    )
    database.commit()
    await query.edit_message_text(t("data_deleted"))


@Client.on_callback_query(filters.regex(r"^delete_data_cancel$"))
@use_chat_lang()
async def delete_data_cancel(c: Client, query: CallbackQuery, t):
    keyboard_buttons = [[(t("back"), "privacy")]]
    await query.edit_message_text(
        t("data_not_deleted"), reply_markup=ikb(keyboard_buttons)
    )
