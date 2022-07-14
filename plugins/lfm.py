import re

from pyrogram import Client, filters

import db
from locales import use_chat_lang
from utils import get_current, get_song_art, get_track_info, http_pool

from .letra import letra

LFM_LINK_RE = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_message(filters.command("lfm"))
@use_chat_lang()
async def lfm(c, m, t):
    text = m.text.split(" ", 1)
    print(text)
    if len(text) == 2:
        db.add_user_last(m.from_user.id, text[1])
        await m.reply_text(t("done"))
    else:
        tk = db.get(m.from_user.id)
        if not tk or not tk[2]:
            await m.reply_text(t("example"))
        else:
            a = await get_current(tk[2])
            if not a:
                await m.reply_text(t("play_playlist"))
            else:
                track_info = await get_track_info(
                    tk[2], a[0]["artist"]["#text"], a[0]["name"]
                )

                stick = db.theme(m.from_user.id)[3]
                mtext = f"🎵 {a[0]['artist']['#text']} - {a[0]['name']}"
                if stick == None or stick:
                    album_url = a[0]["image"][-1]["#text"]
                    if not album_url:
                        # if not present in api return, try to get album url from page
                        r = await http_pool.get(a[0]["url"].replace("/_/", "/"))
                        if r.status_code == 200:
                            album_url = LFM_LINK_RE.findall(r.text)[0]
                        else:
                            r2 = await http_pool.get(a[0]["url"])
                            album_url = LFM_LINK_RE.findall(r2.text)[0]
                    album_art = await get_song_art(
                        song_name=a[0]["name"],
                        artist=a[0]["artist"]["#text"],
                        album_url=album_url,
                        color="dark" if db.theme(m.from_user.id)[0] else "light",
                        blur=db.theme(m.from_user.id)[1],
                        scrobbles=track_info["track"]["userplaycount"],
                    )
                    await m.reply_document(album_art, caption=mtext)
                else:
                    await m.reply(
                        mtext,
                        parse_mode="html",
                    )
                m.text = f"/letra {a[0]['artist']['#text']} {a[0]['name']}"
                await letra(c, m)
