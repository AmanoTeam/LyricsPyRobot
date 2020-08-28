from pyrogram import Client, filters
from plugins.letra import letra
from utils import get_token, get_current_playing
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import db

@Client.on_message(filters.command('spoti'))
async def spoti(c, m):
    text = m.text.split(' ',1)
    if len(text) == 2:
        if 'lyricspy.ml' in text[1]:
            access_code = text[1].split('code=')[1]
        else:
            access_code = text[1]
        res = get_token(m.from_user.id, access_code)
        if res[0]:
            await m.reply_text('Pronto, pode usar o /spoti agora :)')
        else:
            await m.reply_text(f'Ocorreu um erro:\n{res[1]}')
    else:
        tk = db.get(m.from_user.id)
        print(tk)
        if not tk or not tk[0]:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Login', url='https://xn--f77h6a.ml/1ec28a')]
            ])
            await m.reply_text('Use o botão abaixo e faça login. Em copie o comando e mande para mim',reply_markup=kb)
        else:
            a = get_current_playing(m.from_user.id)
            if not a:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em seu Spotify?')
            else:
                await m.reply_text(f"🎶 {a['item']['artists'][0]['name']} - {a['item']['name']}")
                m.text = f"/letra {a['item']['artists'][0]['name']} {a['item']['name']}"
                await letra(c, m)
