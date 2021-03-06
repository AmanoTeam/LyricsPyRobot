import hashlib
import re

from lyricspy.aio import Letras, Musixmatch
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import db

mux = Musixmatch()
let = Letras()

# + original, - traduzido, _ telegraph


@Client.on_message(filters.command("letra"))
async def letra(c, m):
    print('ok')
    text = m.text.split(' ', 1)[1]
    if not text:
        await m.reply_text('**Uso:** /letra <nome da música>')
    elif re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', text):
        a = await let.letra(text)
    elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', text):
        a = await mux.letra(text)
    else:
        a = await mux.auto(text, limit=1)
        if not a:
            a = await let.auto(text, limit=1)
            if not a:
                await m.reply_text('Letra não encontrada :(')
                return True
    a = a[0] if isinstance(a, list) else a
    hash = hashlib.md5(a['link'].encode()).hexdigest()
    db.add_hash(hash, a)
    uid = m.from_user.id
    ma = db.theme(m.from_user.id)[2]
    if not ma:
        if 'traducao' in a:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')] +
                [InlineKeyboardButton(text=a['tr_name'] or 'tradução', callback_data=f'-{uid}|{hash}')]

            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')]
            ])
        await m.reply_text(
            '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096], reply_markup=keyboard, disable_web_page_preview=True)
    else:
        if 'traducao' in a:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Texto', callback_data=f'+{uid}|{hash}')] +
                [InlineKeyboardButton(text=a['tr_name'] or 'tradução', callback_data=f'_-{uid}|{hash}')]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Texto', callback_data=f'+{uid}|{hash}')]
            ])
        await m.reply_text(
            '{} - {}\n{}'.format(a["musica"], a["autor"], db.get_url(hash)[1]), reply_markup=keyboard, parse_mode=None)
