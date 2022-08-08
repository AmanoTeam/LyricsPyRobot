from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales import use_chat_lang


@Client.on_message(filters.command("start"))
@Client.on_callback_query(filters.regex(r"start_back"))
@use_chat_lang()
async def start(c, m, t):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("inline_btn"), switch_inline_query_current_chat=""
                ),
                InlineKeyboardButton(text=t("settings_btn"), callback_data="settings"),
            ]
        ]
    )
    if isinstance(m, filters.CallbackQuery):
        await m.edit_message_text(text=t("start"), reply_markup=keyboard)
    else:
        await m.reply_text(t("start"), reply_markup=keyboard)


@Client.on_message(filters.command("help"))
@use_chat_lang()
async def help(c, m, t):
    await m.reply_text(t("help"))
