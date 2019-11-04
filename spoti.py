import spotipy
import subprocess
from config import keys
from db import dbc, save
from json import loads
from amanobot.namedtuple import InlineKeyboardMarkup
import re
import lyricspy

def spoti(msg,bot):
    db = dbc()
    if msg['text'] == '/spoti':
        if not str(msg['from']['id']) in db:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='Login', url='https://xn--f77h6a.ml/1ec28a')]
                ])
            bot.sendMessage(msg['chat']['id'],'Por favor entre no link a baixo, faça o login e mande o link para mim logo após o comando /spoti',parse_mode='html',reply_markup=kb)
        else:
            a = spotipy.Spotify(auth=db[str(msg['from']['id'])]['access_token'])
            try:
                a = a.current_user_playing_track()
            except:
                b = subprocess.getoutput(f'curl -H "Authorization: Basic {keys["basic"]}" -d grant_type=refresh_token -d refresh_token={db[str(msg["from"]["id"])]["refresh_token"]} https://accounts.spotify.com/api/token')
                b = '{'+b.split('{')[1]
                b = loads(b)
                db[msg['from']['id']] = b
                save(db)
                a = spotipy.Spotify(auth=b['access_token'])
                a = a.current_user_playing_track()
            if a == None:
                bot.sendMessage(msg['chat']['id'],'Você não está tocando nada')
            else:
                bot.sendMessage(msg['chat']['id'],f"todando: {a['item']['album']['artists'][0]['name']} {a['item']['name']}")
                a = lyricspy.auto(f"{a['item']['album']['artists'][0]['name']} {a['item']['name']}",limit=1)[0]
                if a.get('letra'):
                    mik = re.split(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br)', a["link"])[-1]
                    print(mik)
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')]])
                    if a.get('traducao'):
                        teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')] +
                            [dict(text='Tradução', callback_data=f'tr_{mik}|{msg["from"]["id"]}')]])
                    print(teclado)
                    bot.sendMessage(msg['chat']['id'],
                                        '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra']),
                                        reply_to_message_id=msg['message_id'], parse_mode='markdown',
                                        disable_web_page_preview=True, reply_markup=teclado) 
    else:
        text = msg['text'][7:]
        if 'lyricspy.ml' in text:
            a = text.split('code=')[1]
            b = subprocess.getoutput(f'curl -H "Authorization: Basic {keys["basic"]}" -d grant_type=authorization_code -d code={a} -d redirect_uri=https://lyricspy.ml/go https://accounts.spotify.com/api/token')
            b = '{'+b.split('{')[1]
            b = loads(b)
            if 'error' in b:
                bot.sendMessage(msg['chat']['id'],f'ocorreu um erro:\n{b["error"]}')
            else:
                db[msg['from']['id']] = b
                save(db)
                bot.sendMessage(msg['chat']['id'],f'ok')