from lyricspy.aio import letras, muximatch
from pyrogram import Client
from utils import get_current_playing, get_current
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
import hashlib
import db
import json

mux = muximatch()

#+ original, - traduzido, _ telegraph

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
        a = get_current_playing(m.from_user.id)
        if a:
            text = f"{a['item']['artists'][0]['name']} {a['item']['name']}"
            print(text)
            i = await mux.auto(text, limit=1)
            if i:
                i = i[0]
                hash = 's'+hashlib.md5(i["link"].encode()).hexdigest()
                r.update({hash:i["link"]})
                articles.append(InlineQueryResultArticle(
                    title='Current in spotify',
                    description=f'{i["musica"]} - {i["autor"]}'.encode("latin-1", 'ignore').decode("utf-8", 'ignore'),
                    id=hash,
                    thumb_url='https://piics.ml/amn/lpy/spoti.png',
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text='aguarde...',
                    )
                ))
                lm -= 1
    if tk[2]:
        a = get_current(tk[2])
        if a:
            text = f"{a[0]['artist']['#text']} - {a[0]['name']}"
            print(text)
            i = await mux.auto(text, limit=1)
            if i:
                i = i[0]
                hash = 'l'+hashlib.md5(i["link"].encode()).hexdigest()
                r.update({hash:i["link"]})
                articles.append(InlineQueryResultArticle(
                    title='Current in Last.fm',
                    description=f'{i["musica"]} - {i["autor"]}'.encode("latin-1", 'ignore').decode("utf-8", 'ignore'),
                    id=hash,
                    thumb_url='https://piics.ml/amn/lpy/lastfm.png',
                    reply_markup=keyboard,
                    input_message_content=InputTextMessageContent(
                        message_text='aguarde...',
                    )
                ))
                lm -= 1
    if m.query:
        a = await mux.auto(m.query, limit=2)
        for i in a:
            hash = hashlib.md5(i["link"].encode()).hexdigest()
            r.update({hash:i["link"]})
            articles.append(InlineQueryResultArticle(
                title=f'{i["musica"]} - {i["autor"]}'.encode("latin-1", 'ignore').decode("utf-8", 'ignore'),
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
    tk = db.tem(m.from_user.id)
    s = json.loads((tk[0]).replace('\'','\"'))
    text = s[m.result_id]
    a = await mux.letra(text)
    uid = m.from_user.id
    if 'traducao' in a:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')]+
            [InlineKeyboardButton(text=a['tr_name']or'tradução', callback_data=f'-{uid}|{hash}')]

        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{uid}|{hash}')]
        ])
    db.add_hash(hash, a)
    await c.edit_inline_text(m.inline_message_id,'[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096], reply_markup=keyboard, disable_web_page_preview=True)
