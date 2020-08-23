from config import bot, keys
import db
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
from lyricspy.aio import letras, muximatch
import spotipy
from spotipy.client import SpotifyException
import requests
import hashlib

let = letras()
mux = muximatch()

def get_token(user_id, auth_code):
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {keys['basic']}"
                      ),
                      data=dict(
                          grant_type="authorization_code",
                          code=auth_code,
                          redirect_uri="https://lyricspy.ml/go"
                      )).json()
    if b.get("error"):
        return False, b['error']
    else:
        db.add_user(user_id, b['refresh_token'], b['access_token'])
        return True, b['access_token']

def refresh_token(user_id):
    tk = db.get(user_id)
    print(tk[1])
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {keys['basic']}"
                      ),
                      data=dict(
                          grant_type="refresh_token",
                          refresh_token=tk[1]
                      )).json()
    print(b)
    db.update_user(user_id,b['access_token'])
    return b['access_token']

def get_current_playing(user_id):
    tk = db.get(user_id)
    a = spotipy.Spotify(auth=tk[0])
    try:
        return a.current_user_playing_track()
    except SpotifyException:
        new_token = refresh_token(user_id)
        a = spotipy.Spotify(auth=new_token)
        return a.current_user_playing_track()

async def spoti(msg):
    if msg['text'] == '/spoti':
        tk = db.get(msg['from']['id'])
        if not tk[0]:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='Login', url='https://xn--f77h6a.ml/1ec28a')]
            ])
            await bot.sendMessage(msg['chat']['id'],
                            'Use o botão abaixo e faça login. Em seguida, mande o link após o comando /spoti.\n\n'
                            '**Ex.:** ```/spoti https://lyricspy.ml/go?code=AQCan-Nd1Mk2qToUGsIopwV_yOm```',
                            parse_mode='markdown',
                            reply_to_message_id=msg['message_id'],
                            reply_markup=kb)
        else:
            a = get_current_playing(msg['from']['id'])
            if a is None:
                await bot.sendMessage(msg['chat']['id'], 'No momento não há nada tocando. Que tal dar um _play_ em seu Spotify?',
                                parse_mode='markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                await bot.sendMessage(msg['chat']['id'],
                                       f"🎶 {a['item']['artists'][0]['name']} - {a['item']['name']}")
                text = f"{a['item']['artists'][0]['name']} {a['item']['name']}"
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
        if 'lyricspy.ml' in text:
            access_code = text.split('code=')[1]
        else:
            access_code = text
        res = get_token(msg['from']['id'], access_code)
        if res[0]:
            await bot.sendMessage(msg['chat']['id'], f'ok')
        else:
            await bot.sendMessage(msg['chat']['id'], f'ocorreu um erro:\n{res[1]}')

async def ainline(msg):
    r = {}
    a = get_current_playing(msg['from']['id'])
    if a is None:
        articles = [InlineQueryResultArticle(
            id='spoti',
            title='spoti: Você não está tocando nada',
            thumb_url='https://piics.ml/amn/lpy/spoti.png',
            input_message_content=InputTextMessageContent(
                message_text="Você não está tocando nada"))]
    else:
        text = f"{a['item']['artists'][0]['name']} {a['item']['name']}"
        print(text)
        a = await mux.auto(text, limit=1)
        print(a)
        if not a:
            print(a)
            a = await let.auto(text, limit=1)
            if not a:
                articles = [InlineQueryResultArticle(
                    id='spoti',
                    title='spoti: Letra não encontrada',
                    thumb_url='https://piics.ml/amn/lpy/spoti.png',
                    input_message_content=InputTextMessageContent(
                        message_text="Não foi possivel achar letra"))]
                return r, articles
        a = a[0]
        hash = hashlib.md5(a['link'].encode()).hexdigest()
        r.update({hash:a['link']})
        teclado = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='Aguarde...', callback_data='a')]
        ])
        articles = [InlineQueryResultArticle(
            id=hash,
            title=f'spoti: {a["musica"]} - {a["autor"]}',
            thumb_url='https://piics.ml/i/010.png',
            reply_markup=teclado,
            input_message_content=InputTextMessageContent(
                message_text='Aguarde...',
                parse_mode='markdown', disable_web_page_preview=True))]
        db.tem(msg['from']['id'], r)
    return r, articles