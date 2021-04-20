import hashlib
import re

from lyricspy.aio import Letras, Musixmatch
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locale import use_chat_lang

import db
from config import MUSIXMATCH_KEYS

mux = Musixmatch(usertoken=MUSIXMATCH_KEYS)
let = Letras()

# + original, - traduzido, _ telegraph


@Client.on_message(filters.command(["lyrics", "letra"]))
@use_chat_lang()
async def letra(c, m, t):
    text = m.text.split(' ', 1)[1]
    if not text:
        await m.reply_text(t('use'))
    elif re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', text):
        a = await let.letra(text)
    elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', text):
        a = await mux.lyrics(text)
    else:
        a = await mux.auto(text, limit=1, lang='pt')
        if not a:
            a = await let.auto(text, limit=1)
            if not a:
                await m.reply_text(t('lyrics_nf'))
                return True
    a = a[0] if isinstance(a, list) else a
    if 'art' in a:
        a = let.parce(a)
    else:
        a = mux.parce(a)
    hash = str(a['id'])
    db.add_hash(hash, a)
    uid = m.from_user.id
    ma = db.theme(m.from_user.id)[2]
    if not ma:
        if a['traducao']:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t('tgph'), callback_data=f'_+{uid}|{hash}')] +
                [InlineKeyboardButton(text=t('port'), callback_data=f'-{uid}|{hash}')]

            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t('tgph'), callback_data=f'_+{uid}|{hash}')]
            ])
        await m.reply_text(
            '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096], reply_markup=keyboard, disable_web_page_preview=True)
    else:
        if a['traducao']:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t('text'), callback_data=f'+{uid}|{hash}')] +
                [InlineKeyboardButton(text=t('port'), callback_data=f'_-{uid}|{hash}')]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t('text'), callback_data=f'+{uid}|{hash}')]
            ])
        await m.reply_text(
            '{} - {}\n{}'.format(a["musica"], a["autor"], db.get_url(hash)[1]), reply_markup=keyboard, parse_mode=None)
