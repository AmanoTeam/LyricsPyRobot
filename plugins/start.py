from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start(c: Client, m: Message):
    await m.reply("Hello")