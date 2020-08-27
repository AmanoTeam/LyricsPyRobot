from pyrogram import Client, filters
from plugins.letra import letra
from utils import get_current
import db

@Client.on_message(filters.command('lfm'))
async def lfm(c ,m):
    text = m.text.split(' ',1)
    print(text)
    if len(text) == 2:
        db.add_user_last(m.from_user.id, text[1])
        await m.reply_text('Pronto, pode usar o /lfm agora :)')
    else:
        tk = db.get(m.from_user.id)
        if not tk[2]:
            await m.reply_text('Mande seu user do last.fm após o /lfm.\n\n'
                               '**Ex.:** ```/lfm alisson```')
        else:
            a = get_current(tk[2])
            if not a:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em sua playlist?')
            else:
                await m.reply_text(f"🎶 {a[0]['artist']['#text']} - {a[0]['name']}")
                m.text = f"/letra {a[0]['artist']['#text']} {a[0]['name']}"
                await letra(c, m)
    