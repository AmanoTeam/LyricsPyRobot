import asyncio

from hydrogram import Client, idle

from config import API_HASH, API_ID, TOKEN
from lyricspybot.utils import browser, event_loop, http_client, musixmatch_client

asyncio.set_event_loop(event_loop)


async def main():
    await client.start()

    await idle()

    await client.stop()
    await http_client.aclose()
    await musixmatch_client.http.aclose()
    await browser.close()


client = Client(
    "bot",
    API_ID,
    API_HASH,
    bot_token=TOKEN,
    plugins={"root": "lyricspybot.plugins"},
    workdir=".",
)

if __name__ == "__main__":
    event_loop.run_until_complete(main())
