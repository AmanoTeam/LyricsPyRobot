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
                [InlineKeyboardButton(text='Login', url='https://accounts.spotify.com/authorize?response_type=code&'+
                                                                                        'client_id=6fa50508cfdc4d1490ce8cf29d12097a&'+
                                                                                        'scope=user-read-currently-playing+user-modify-playback-state+user-read-playback-state&'+
                                                                                        'redirect_uri=https://lyricspy.amanoteam.com/go')]
            ])
            await m.reply_text('Use o botão abaixo e faça login. Em copie o comando e mande para mim', reply_markup=kb)
        else:
            sess = await get_spoti_session(m.from_user.id)
            spotify_json = sess.current_user_playing_track()
            if not spotify_json:
                await m.reply_text('No momento não há nada tocando. Que tal dar um __play__ em seu Spotify?')
            else:
                stick = db.theme(m.from_user.id)[3]
                if stick == None or stick:
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
                    if stick == None or stick:
                        await m.reply_sticker(album_art, reply_markup=kb)
                    else:
                        await m.reply(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}", reply_markup=kb)
                else:
                    if stick == None or stick:
                        await m.reply_sticker(album_art)
                    else:
                        await m.reply(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}")
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
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        print(dir(m))
        sess.previous_track(device_id)
        spotify_json = sess.current_user_playing_track()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        spotify_json = sess.current_user_playing_track()
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}", reply_markup=kb)
        else:
            await m.answer(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}")
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mexer nisso, somente o {a.first_name} pode')

@Client.on_callback_query(filters.regex(r'^next'))
async def next(c, m):
    print(m.data)
    print('next')
    user = m.data.split('|')[1]
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        print(dir(m))
        sess.next_track(device_id)
        spotify_json = sess.current_user_playing_track()
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if spotify_json['is_playing'] else '▶️', callback_data=f'pause|{m.from_user.id}' if spotify_json['is_playing'] else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        spotify_json = sess.current_user_playing_track()
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}", reply_markup=kb)
        else:
            await m.answer(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}")
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mexer nisso, somente o {a.first_name} pode')

@Client.on_callback_query(filters.regex(r'^(pause|play)'))
async def ppa(c, m):
    print(m.data)
    cmd, user = m.data.split('|')
    if m.from_user.id == int(user):
        sess = await get_spoti_session(m.from_user.id)
        devices = sess.devices()
        for i in devices['devices']:
            if i['is_active']:
                device_id = i['id']
                break
        if 'pause' in cmd:
            print('pause')
            sess.pause_playback(device_id)
        else:
            print('play')
            sess.start_playback(device_id)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏮', callback_data=f'previous|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏸' if 'play' in cmd else '▶️', callback_data=f'pause|{m.from_user.id}' if 'play' in cmd else f'play|{m.from_user.id}')] +
            [InlineKeyboardButton(text='⏭', callback_data=f'next|{m.from_user.id}')]
        ])
        spotify_json = sess.current_user_playing_track()
        if not db.theme(m.from_user.id)[3]:
            await m.edit_message_text(f"Tocando: {spotify_json['item']['artists'][0]['name']} - {spotify_json['item']['name']}", reply_markup=kb)
        else:
            await m.edit_message_reply_markup(reply_markup=kb)
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mexer nisso, somente o {a.first_name} pode')
