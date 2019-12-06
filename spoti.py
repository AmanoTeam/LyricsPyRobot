import re

import lyricspy
import markdown2
import requests
import spotipy
from spotipy.client import SpotifyException
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
from telegraph import Telegraph

from config import keys
from db import dbc, save

telegraph = Telegraph()
telegraph.create_account(short_name='LyricsPyRobot', author_name='amn')


def send_te(a, b):
    response = telegraph.create_page(
        a['musica'],
        html_content=markdown2.markdown(b.replace('\n', '<br>')),
        author_name=a["autor"],
        author_url=a["link"]
    )
    return response

def inline(msg, bot):
    db = dbc()
    a = get_current_playing(str(msg['from']['id']), db)
    if a is None:
        articles = [InlineQueryResultArticle(
            id='a',
            title='spoti: Você não está tocando nada',
            thumb_url='https://piics.ml/amn/lpy/spoti.png',
            input_message_content=InputTextMessageContent(
                message_text="Você não está tocando nada")
        )]
    else:
        a = lyricspy.auto(f"{a['item']['album']['artists'][0]['name']} {a['item']['name']}", limit=1)[0]
        teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Aguarde...', callback_data='a')]])
        articles = [InlineQueryResultArticle(
            id=a['link'],
            thumb_url='https://piics.ml/amn/lpy/spoti.png',
            title=f'spoti: {a["musica"]} - {a["autor"]}',
            input_message_content=InputTextMessageContent(
                message_text='Aguarde...',
                parse_mode='markdown', disable_web_page_preview=True),
            reply_markup=teclado)]
    return articles


def refresh_token(user_id, db):
    b = requests.post("https://accounts.spotify.com/api/token",
                      headers=dict(
                          Authorization=f"Basic {keys['basic']}"
                      ),
                      data=dict(
                          grant_type="refresh_token",
                          refresh_token=db[str(user_id)]["refresh_token"]
                      )).json()
    db[str(user_id)]['access_token'] = b['access_token']
    save(db)
    return b['access_token']


def get_token(user_id, auth_code, db):
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
        db[str(user_id)] = b
        save(db)
        return True, b['access_token']


def get_current_playing(user_id, db):
    a = spotipy.Spotify(auth=db[user_id]['access_token'])
    try:
        return a.current_user_playing_track()
    except SpotifyException:
        new_token = refresh_token(user_id, db)
        a = spotipy.Spotify(auth=new_token)
        return a.current_user_playing_track()


def spoti(msg, bot):
    db = dbc()
    if msg['text'] == '/spoti':
        if not str(msg['from']['id']) in db:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [dict(text='Login', url='https://xn--f77h6a.ml/1ec28a')]
            ])
            bot.sendMessage(msg['chat']['id'],
                            'Use o botão abaixo e faça login. Em seguida, mande o link após o comando /spoti.\n\n'
                            '**Ex.:** ```/spoti https://lyricspy.ml/go?code=AQCan-Nd1Mk2qToUGsIopwV_yOm```',
                            parse_mode='markdown',
                            reply_to_message_id=msg['message_id'],
                            reply_markup=kb)
        else:
            a = get_current_playing(str(msg['from']['id']), db)
            if a is None:
                bot.sendMessage(msg['chat']['id'], 'No momento não há nada tocando. Que tal dar um _play_ em seu Spotify?',
                                parse_mode='markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                sent = bot.sendMessage(msg['chat']['id'],
                                       f"🎶 {a['item']['album']['artists'][0]['name']} - {a['item']['name']}")
                a = lyricspy.auto(f"{a['item']['album']['artists'][0]['name']} {a['item']['name']}", limit=1)
                if a:
                    a = a[0]
                    mik = re.split(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br)', a["link"])[-1]
                    text = '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])
                    if len(text) > 4096:
                        text = send_te(a, a['letra'])['url']
                        if a.get('traducao'):
                            teclado = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='Traducão', callback_data=f"tell_{mik}|{msg['from']['id']}")]])
                    else:
                        teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')]])
                        if a.get('traducao'):
                            teclado = InlineKeyboardMarkup(inline_keyboard=[
                                [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')] +
                                [dict(text='Tradução', callback_data=f'tr_{mik}|{msg["from"]["id"]}')]])
                    print(text)
                    bot.sendMessage(msg['chat']['id'],
                                        text,
                                        reply_to_message_id=msg['message_id'], parse_mode='markdown',
                                        disable_web_page_preview=True, reply_markup=teclado)
                else:
                    bot.sendMessage(msg['chat']['id'],
                                    "Letra não encontrada :(",
                                    reply_to_message_id=sent['message_id'])
    else:
        text = msg['text'][7:]
        if 'lyricspy.ml' in text:
            access_code = text.split('code=')[1]
            res = get_token(msg['from']['id'], access_code, db)
            if res[0]:
                bot.sendMessage(msg['chat']['id'], f'ok')
            else:
                bot.sendMessage(msg['chat']['id'], f'ocorreu um erro:\n{res[1]}')
