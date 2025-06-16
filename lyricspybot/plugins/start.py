from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from lyricspybot.locales import use_chat_lang


@Client.on_message(filters.command("start") & ~filters.regex(r"start "), group=1)
@Client.on_callback_query(filters.regex(r"start_back"))
@use_chat_lang()
async def start(c, m: Message | CallbackQuery, t):
    """
    Welcome message and initial bot menu.
    """
    if not isinstance(m, CallbackQuery) and m.chat.type != ChatType.PRIVATE:
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("inline_btn"),
                        switch_inline_query_current_chat="",
                    ),
                ]
            ]
        )
    else:
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("settings_btn"), callback_data="settings"
                    ),
                    InlineKeyboardButton(text=t("donate_btn"), callback_data="donate"),
                ],
                [
                    InlineKeyboardButton(
                        text=t("inline_btn"),
                        switch_inline_query_current_chat="",
                    ),
                ],
            ]
        )

    if isinstance(m, CallbackQuery):
        await m.edit_message_text(text=t("start"), reply_markup=inline_keyboard)
    else:
        await m.reply_text(t("start"), reply_markup=inline_keyboard)


@Client.on_message(filters.command("help"))
@use_chat_lang()
async def help_command(c: Client, m: Message, t):
    """
    Displays the help message with available commands.
    """
    await m.reply_text(t("help"))
