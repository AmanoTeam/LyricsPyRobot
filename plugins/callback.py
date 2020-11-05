import re

from lyricspy.aio import letras, muximatch
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import db
from config import sudos

mux = muximatch()
let = letras()


# + original, - traduzido, _ telegraph


@Client.on_callback_query(filters.regex(r'^(_\+)'))
async def teor(c, m):
    user, hash = m.data[2:].split('|')
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        if not n:
            await m.answer('Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', n[0]):
                a = await let.letra(n[0])
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', n[0]):
                a = await mux.letra(n[0])
            else:
                await m.answer(f'link inválido:\n{n[0]}', show_alert=True)
                return True
            if n[2]:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Texto', callback_data=f'+{user}|{hash}')] +
                    [InlineKeyboardButton(text=a['tr_name'] or 'tradução', callback_data=f'_-{user}|{hash}')]
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Texto', callback_data=f'+{user}|{hash}')]
                ])
            await m.edit_message_text(
                '{} - {}\n{}'.format(a["musica"], a["autor"], n[1]).encode("latin-1", 'backslashreplace').decode(
                    "unicode_escape"), reply_markup=keyboard)
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mecher nisso, somente o {a.first_name} {a.last_name} pode')


@Client.on_callback_query(filters.regex(r"^(_\-)"))
async def tetr(c, m):
    user, hash = m.data[2:].split('|')
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        if not n:
            await m.answer('Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', n[0]):
                a = await let.letra(n[0])
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', n[0]):
                a = await mux.letra(n[0])
            else:
                await m.answer(f'link inválido:\n{n[0]}', show_alert=True)
                return True
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Texto', callback_data=f'-{user}|{hash}')] +
                [InlineKeyboardButton(text='Original', callback_data=f'_+{user}|{hash}')]
            ])
            await m.edit_message_text(
                '{} - {}\n{}'.format(a["musica"], a["autor"], n[2]).encode("latin-1", 'backslashreplace').decode(
                    "unicode_escape"), reply_markup=keyboard)
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mecher nisso, somente o {a.first_name} {a.last_name} pode')


@Client.on_callback_query(filters.regex(r"^(\+)"))
async def ori(c, m):
    user, hash = m.data[1:].split('|')
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        if not n:
            await m.answer('Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', n[0]):
                a = await let.letra(n[0])
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', n[0]):
                a = await mux.letra(n[0])
            else:
                await m.answer(f'link inválido:\n{n[0]}', show_alert=True)
                return True
            if n[2]:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{user}|{hash}')] +
                    [InlineKeyboardButton(text=a['tr_name'] or 'traducao', callback_data=f'-{user}|{hash}')]
                ])
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]
                ])
            await m.edit_message_text(
                '[{} - {}]({})\n{}'.format(a["musica"], a["autor"],
                                           a['link'], a['letra']).encode("latin-1", 'backslashreplace')
                                                                 .decode("unicode_escape")[:4096],
                reply_markup=keyboard, disable_web_page_preview=True)
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mecher nisso, somente o {a.first_name} {a.last_name} pode')


@Client.on_callback_query(filters.regex(r"^(\-)"))
async def tr(c, m):
    user, hash = m.data[1:].split('|')
    if m.from_user.id == int(user) or m.from_user.id in sudos:
        n = db.get_url(hash)
        if not n:
            await m.answer('Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', n[0]):
                a = await let.letra(n[0])
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', n[0]):
                a = await mux.letra(n[0])
            else:
                await m.answer(f'link inválido:\n{n[0]}', show_alert=True)
                return True
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Telegra.ph', callback_data=f'_-{user}|{hash}')] +
                [InlineKeyboardButton(text='Original', callback_data=f'+{user}|{hash}')]
            ])
            await m.edit_message_text(
                '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['traducao'])[:4096].encode("latin-1",
                                                                                                            'backslashreplace').decode(
                    "unicode_escape"), reply_markup=keyboard, disable_web_page_preview=True)
    else:
        a = await c.get_chat(int(user))
        await m.answer(f'Você n pode mecher nisso, somente o {a.first_name} {a.last_name} pode')
