import hashlib
import json

from lyricspy.aio import Musixmatch
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

import db
from config import MUSIXMATCH_KEYS
from utils import get_spoti_session, get_current

mux = Musixmatch(usertoken=MUSIXMATCH_KEYS)

# + original, - traduzido, _ telegraph


@Client.on_inline_query()
async def inline(c, m):
    print(m.query)
    tk = db.get(m.from_user.id)
    articles = []
    r = {}
    lm = 4
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='aguarde...', callback_data='a')]
    ])
    if tk[0]:
        sess = await get_spoti_session(m.from_user.id)
        a = sess.current_user_playing_track()
        if a:
            text = f"{a['item']['artists'][0]['name']} {a['item']['name']}"
            print(text)
            i = await mux.auto(text, limit=1, lang='pt')
            if i:
                i = mux.parce(i[0])
                hash = 's' + str(i['id'])
                r.update({hash: i["link"]})
                articles.append(InlineQueryResultArticle(
                    title='Current in spotify',
                    description=f'{i["musica"]} - {i["autor"]}',
                    id=hash,
                    thumb_url='https://piics.ml/amn/lpy/spoti.png',
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text='aguarde...',
                    )
                ))
                lm -= 1
    if tk[2]:
        a = await get_current(tk[2])
        if a:
            text = f"{a[0]['artist']['#text']} - {a[0]['name']}"
            print(text)
            i = await mux.auto(text, limit=1, lang='pt')
            if i:
                i = mux.parce(i[0])
                hash = 'l' + str(i['id'])
                r.update({hash: i["link"]})
                articles.append(InlineQueryResultArticle(
                    title='Current in Last.fm',
                    description=f'{i["musica"]} - {i["autor"]}',
                    id=hash,
                    thumb_url='https://piics.ml/amn/lpy/lastfm.png',
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text='aguarde...',
                    )
                ))
                lm -= 1
    if m.query:
        a = await mux.auto(m.query, limit=2, lang='pt')
        for i in a:
            i = mux.parce(i)
            hash = str(i['id'])
            r.update({hash: i["link"]})
            articles.append(InlineQueryResultArticle(
                title=f'{i["musica"]} - {i["autor"]}',
                id=hash,
                thumb_url='https://piics.ml/i/010.png',
                reply_markup=keyboard,
                input_message_content=InputTextMessageContent(
                    message_text='aguarde...',
                )
            ))
    db.tem(m.from_user.id, r)
    await m.answer(articles)


@Client.on_chosen_inline_result()
async def choosen(c, m):
    if m.result_id[0] == 's' or m.result_id[0] == 'l':
        hash = m.result_id[1:]
    else:
        hash = m.result_id
    a = await mux.lyrics(hash)
    a = mux.parce(a)
    uid = m.from_user.id
    ma = db.theme(uid)[2]
    if not ma:
        if a['traducao']:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')] +
                [InlineKeyboardButton(text='Português', callback_data=f'-{uid}|{hash}')]

            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')]
            ])
        db.add_hash(hash, a)
        await c.edit_inline_text(m.inline_message_id,
                                '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096], reply_markup=keyboard,
                                disable_web_page_preview=True)
    else:
        if a['traducao']:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Texto', callback_data=f'+{uid}|{hash}')] +
                [InlineKeyboardButton(text='Português', callback_data=f'_-{uid}|{hash}')]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Texto', callback_data=f'+{uid}|{hash}')]
            ])
        await c.edit_inline_text(m.inline_message_id,
            '{} - {}\n{}'.format(a["musica"], a["autor"], db.get_url(hash)[1]), reply_markup=keyboard, parse_mode=None)
