from lyricspy.aio import letras, muximatch
from pyrogram import Client, Filters, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
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
    #if tk[0]:
    #    spoti
    #if tk[1]:
    #    lfm
    if m.query:
        a = await mux.auto(m.query)
        for i in a:
            hash = hashlib.md5(i["link"].encode()).hexdigest()
            r.update({hash:i["link"]})
            keybpard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='aguarde...', callback_data='a')]
            ])
            articles.append(InlineQueryResultArticle(
                title=f'{i["musica"]} - {i["autor"]}',
                id=hash,
                thumb_url='https://piics.ml/i/010.png',
                reply_markup=keybpard,
                input_message_content=InputTextMessageContent(
                    message_text='aguarde...',
                )
            ))
        db.tem(m.from_user.id, r)
    await m.answer(articles)

@Client.on_chosen_inline_result()
async def choosen(c, m):
    tk = db.tem(m.from_user.id)
    s = json.loads((tk[0]).replace('\'','\"'))
    hash = m.result_id
    text = s[hash]
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