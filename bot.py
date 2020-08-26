import asyncio
from config import TOKEN, API_HASH, API_ID
from pyrogram import Client

async def main(client):
    await client.start()
    await client.idle()

client = Client("bot", API_ID, API_HASH, bot_token=TOKEN, plugins=dict(root='plugins'))

loop = asyncio.get_event_loop()
loop.run_until_complete(main(client))