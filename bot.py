import asyncio

from hydrogram import Client, idle

from config import API_HASH, API_ID, TOKEN
from utils import browser, http_pool, letras, loop, musixmatch

asyncio.set_event_loop(loop)


async def main():
    await client.start()

    await idle()

    await client.stop()
    await http_pool.aclose()
    await letras.http.aclose()
    await musixmatch.http.aclose()
    await browser.close()


client = Client("bot", API_ID, API_HASH, bot_token=TOKEN, plugins={"root": "plugins"})

if __name__ == "__main__":
    loop.run_until_complete(main())
