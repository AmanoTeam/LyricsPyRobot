import asyncio

from pyrogram import Client, idle

from config import API_HASH, API_ID, TOKEN
from utils import http_pool, webdrv


async def main():
    await client.start()

    await idle()

    await client.stop()
    await http_pool.aclose()
    webdrv.close()


client = Client("bot", API_ID, API_HASH, bot_token=TOKEN, plugins=dict(root="plugins"))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
