from pyrogram import Client, filters
from .letra import letra
from utils import get_token, get_spoti_session, get_song_art
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import db


@Client.on_message(filters.command('spoti') | filters.command('np'))
async def spoti(c, m):
    text = m.text.split(' ', 1)
    if len(text) == 2:
        if 'code=' in text[1]:
            access_code = text[1].split('code=')[1]
        else:
            access_code = text[1]
        res = await get_token(m.from_user.id, access_code)
        if res[0]:
            await m.reply_text('Pronto, pode usar o /spoti ou /np agora :)')
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
            sess = await get_spoti_session(m.from_user.id)
            spotify_json = sess.current_user_playing_track()
            if not spotify_json:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em seu Spotify?')
            else:
                album_art = await get_song_art(song_name=spotify_json['item']['name'],
                                               artist=spotify_json['item']['artists'][0]['name'],
                                               album_url=spotify_json['item']['album']['images'][0]['url'],
                                               duration=spotify_json['item']['duration_ms'] // 1000,
                                               progress=spotify_json['progress_ms'] // 1000,
                                               color="dark" if db.theme(m.from_user.id)[0] else "light",
                                               blur=db.theme(m.from_user.id)[1])
                if 'np' in text[0]:
                    kb = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
                        [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
                        [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
                    ])
                    await m.reply_sticker(album_art, reply_markup=kb)
                else:
                    await m.reply_sticker(album_art)
                    m.text = f"/letra {spotify_json['item']['artists'][0]['name']} {spotify_json['item']['name']}"
                    await letra(c, m)

@Client.on_callback_query(filters.regex(r'^previous'))
async def previous(c, m):
    print(m.data)
    print('prev')
    user = m.data.split('|')[1]
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        spotify_json = sess.current_user_playing_track()
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        print(dir(m))
        sess.previous_track(device_id)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        await m.edit_message_reply_markup(reply_markup=kb)

@Client.on_callback_query(filters.regex(r'^next'))
async def next(c, m):
    print(m.data)
    print('next')
    user = m.data.split('|')[1]
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        spotify_json = sess.current_user_playing_track()
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        print(dir(m))
        sess.next_track(device_id)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        await m.edit_message_reply_markup(reply_markup=kb)

@Client.on_callback_query(filters.regex(r'^(pause|play)'))
async def ppa(c, m):
    print(m.data)
    cmd, user = m.data.split('|')
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        spotify_json = sess.current_user_playing_track()
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        if spotify_json['is_playing']:
            print('pause')
            sess.pause_playback(device_id)
        else:
            print('play')
            sess.start_playback(device_id)
        spotify_json = sess.current_user_playing_track()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        await m.edit_message_reply_markup(reply_markup=kb)