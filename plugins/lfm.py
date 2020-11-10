import re
from pyrogram import Client, filters

import db
from plugins.letra import letra
from utils import get_current, get_song_art, http_pool


LFM_LINK_RE = re.compile(r'<meta property=\"og:image\" +?content=\"(.+)\"')


@Client.on_message(filters.command('lfm'))
async def lfm(c, m):
    text = m.text.split(' ', 1)
    print(text)
    if len(text) == 2:
        db.add_user_last(m.from_user.id, text[1])
        await m.reply_text('Pronto, pode usar o /lfm agora :)')
    else:
        tk = db.get(m.from_user.id)
        if not tk or not tk[2]:
            await m.reply_text('Mande seu user do last.fm após o /lfm.\n\n'
                               '**Ex.:** ```/lfm alisson```')
        else:
            a = await get_current(tk[2])
            if not a:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em sua playlist?')
            else:
                album_url = a[0]['image'][-1]['#text']
                if not album_url:
                    # if not present in api return, try to get album url from page
                    r = await http_pool.get(a[0]['url'].replace('/_/', '/'))
                    if r.status_code == 200:
                        album_url = LFM_LINK_RE.findall(r.text)[0]
                    else:
                        r2 = await http_pool.get(a[0]['url'])
                        album_url = LFM_LINK_RE.findall(r2.text)[0]

                album_art = await get_song_art(song_name=a[0]['name'],
                                               artist=a[0]['artist']['#text'],
                                               album_url=album_url,
                                               color="dark" if db.theme(m.from_user.id)[0] else "light",
                                               blur=db.theme(m.from_user.id)[1])
                await m.reply_sticker(album_art)
                m.text = f"/letra {a[0]['artist']['#text']} {a[0]['name']}"
                await letra(c, m)
