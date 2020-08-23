from plugins.spoti import ainline
import db
from config import bot
from lyricspy.aio import muximatch
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
import hashlib

mux = muximatch()

async def inline(msg):
    print(msg['query'])
    tk = db.get(msg['from']['id'])
    if tk[0]:
        r, articles = await ainline(msg)
    else:
        r, articles = {}, []
    if msg['query'] != '':
        a = await mux.auto(msg['query'])
        for i in a:
            hash = hashlib.md5(i['link'].encode()).hexdigest()
            r.update({hash:i['link']})
            teclado = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='Aguarde...', callback_data='a')]
            ])
            articles.append(InlineQueryResultArticle(
                id=hash,
                title=f'{i["musica"]} - {i["autor"]}',
                thumb_url='https://piics.ml/i/010.png',
                reply_markup=teclado,
                input_message_content=InputTextMessageContent(
                    message_text='Aguarde...',
                    parse_mode='markdown', disable_web_page_preview=True))
            )
        db.tem(msg['from']['id'], r)
    print(r)
    await bot.answerInlineQuery(msg['id'], results=articles, is_personal=True, cache_time=0)