import db
import json
from lyricspy.aio import letras, muximatch
import re
from amanobot.namedtuple import InlineKeyboardMarkup
from config import bot

mux = muximatch()
let = letras()

async def chosen(msg):
    tk = db.tem(msg['from']['id'])
    m = json.loads((tk[0]).replace('\'','\"'))
    hash = msg['result_id']
    text = m[hash]
    print(text)
    if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', text):
        a = await let.letra(text)
    elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', text):
        a = await mux.letra(text)
    else:
        return True
    print(a)
    user= msg['from']['id']
    if 'traducao' in a:
        teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]+[dict(text=a['tr_name']or'tradução', callback_data=f'-{user}|{hash}')]])
    else:
        teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]])
    await bot.editMessageText(msg['inline_message_id'],
                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
    db.add_hash(hash,a)