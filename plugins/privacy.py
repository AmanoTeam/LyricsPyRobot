from hydrogram import Client, filters
from pyrogram.types import Message

from locales import use_chat_lang

@Client.on_message(filters.command("privacy"))
@use_chat_lang()
async def privacy(c: Client, m: Message, t):
    await m.reply(t("privacy"))