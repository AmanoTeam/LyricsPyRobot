from pyrogram import Client, idle
from config import BOT_CONFIG
import asyncio

client = Client(session_name="LyricsPy",
                api_id=BOT_CONFIG["API_ID"],
                bot_token=BOT_CONFIG["TOKEN"],
                api_hash=BOT_CONFIG["API_HASH"],
                plugins=dict(root="plugins"))

async def main():
    await client.start()

    await idle()

    await client.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
