from config import BROWSER
from selenium import webdriver
from pyrogram import Client, filters
from .letra import letra
from utils import get_token, get_current_playing, get_song_art, build_webdriver_object
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import time
import db
import os


webdrv = build_webdriver_object(BROWSER)


@Client.on_message(filters.command('spoti'))
async def spoti(c, m):
    text = m.text.split(' ', 1)
    if len(text) == 2:
        if 'code=' in text[1]:
            access_code = text[1].split('code=')[1]
        else:
            access_code = text[1]
        res = get_token(m.from_user.id, access_code)
        if res[0]:
            await m.reply_text('Pronto, pode usar o /spoti agora :)')
        else:
            await m.reply_text(f'Ocorreu um erro:\n{res[1]}')
    else:
        tk = db.get(m.from_user.id)
        print(tk)
        if not tk or not tk[0]:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Login', url='https://xn--f77h6a.ml/1ec28a')]
            ])
            await m.reply_text('Use o botão abaixo e faça login. Em copie o comando e mande para mim', reply_markup=kb)
        else:
            spotify_json = get_current_playing(m.from_user.id)
            if not spotify_json:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em seu Spotify?')
            else:
                album_art = await get_song_art(webdrv,
                                               song_name=spotify_json['item']['name'],
                                               artist=spotify_json['item']['artists'][0]['name'],
                                               album_url=spotify_json['item']['album']['images'][0]['url'],
                                               duration=spotify_json['item']['duration_ms'] // 1000,
                                               progress=spotify_json['progress_ms'] // 1000,
                                               color="dark" if db.theme(m.from_user.id)[0] else "light",
                                               blur=db.theme(m.from_user.id)[1])
                await m.reply_sticker(album_art)
                m.text = f"/letra {spotify_json['item']['artists'][0]['name']} {spotify_json['item']['name']}"
                await letra(c, m)
