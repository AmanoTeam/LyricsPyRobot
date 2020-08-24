import requests
import db
from config import bot
from lyricspy.aio import letras, muximatch
import hashlib
from amanobot.namedtuple import InlineKeyboardMarkup

let = letras()
mux = muximatch()

def get_current(user):
    r = requests.get('http://ws.audioscrobbler.com/2.0/',params=dict(
        method='user.getrecenttracks',
        user=user,
        api_key='7ab7205cd45f3aa6a5ed89e0ac262c4d',
        format='json',
        limit=1))
    return r.json()['recenttracks']['track']

r = get_current('edubr029')

async def lastfm(msg):
    if msg['text'] == '/lfm':
        tk = db.get(msg['from']['id'])
        if not tk[2]:
            await bot.sendMessage(msg['chat']['id'],
                            'Mande seu user do last.fm após o /lfm.\n\n'
                            '**Ex.:** ```/lfm alisson```',
                            parse_mode='markdown',
                            reply_to_message_id=msg['message_id'])
        else:
            a = get_current(tk[2])
            if not a:
                await bot.sendMessage(msg['chat']['id'], 'No momento não há nada tocando. Que tal dar um _play_ em sua playlist?',
                                parse_mode='markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'],
                                      f"🎶 {a[0]['artist']['#text']} - {a[0]['name']}")
                text = f"{a[0]['artist']['#text']} {a[0]['name']}"
                print(text)
                a = await mux.auto(text, limit=1)
                if not a:
                    a = await let.auto(text, limit=1)
                    if not a:
                        await bot.sendMessage(msg['chat']['id'],
                                        'Letra não encontrada :(',reply_to_message_id=msg['message_id'])
                        return True
                a = a[0]
                hash = hashlib.md5(a['link'].encode()).hexdigest()
                db.add_hash(hash, a)
                user = msg['from']['id']
                if 'traducao' in a:
                    teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]+[dict(text=a['tr_name']or'tradução', callback_data=f'-{hash}')]])
                else:
                    teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]])
                await bot.sendMessage(msg['chat']['id'],
                                '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096]
                                ,reply_to_message_id=msg['message_id'], disable_web_page_preview=True, reply_markup=teclado, parse_mode='markdown')
    else:
        text = msg['text'].split(' ',1)[1]
        db.add_user_last(msg['from']['id'], text)
        await bot.sendMessage(msg['chat']['id'], 'ok')
