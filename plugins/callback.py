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
                    "unicode_escape"), reply_markup=keyboard, parse_mode=None)
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
                    "unicode_escape"), reply_markup=keyboard, parse_mode=None)
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


@Client.on_callback_query(filters.regex(r"settings"))
async def settings(c, m):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Tema", callback_data="theme")] +
        [InlineKeyboardButton(text="Idioma (SOON)", callback_data='language')] +
        [InlineKeyboardButton(text="Padrão", callback_data="pattern")]
    ])
    await m.edit_message_text(
        'Você gostaria de configurar o quê?', reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"language"))
async def lang(c, m):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Voltar', callback_data="settings")]
    ])
    await m.edit_message_text(
        'Em Breve...', reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"theme"))
async def theme(c, m):
    a = db.theme(m.from_user.id)
    if a[0] is None or '_' in m.data and a[0]:
        tid = False
    elif '_' in m.data and not a[0]:
        tid = True
    else:
        tid = a[0]
    if a[1] is None or '-' in m.data and not a[1]:
        bid = True
    elif '-' in m.data and a[1]:
        bid = False
    else:
        bid = a[1]
    tname = ['light', 'dark']
    bname = ['off', 'on']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Tema: ', callback_data='none')] +
        [InlineKeyboardButton(text=tname[tid], callback_data='theme_')],
        [InlineKeyboardButton(text='Blur: ', callback_data='none')] +
        [InlineKeyboardButton(text=bname[bid], callback_data='theme-')],
        [InlineKeyboardButton(text='Voltar', callback_data="settings")]
    ])
    db.def_theme(m.from_user.id, tid, bid, a[2])
    await m.edit_message_text(
        'Escolha em baixo:', reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"pattern"))
async def pattern(c, m):
    a = db.theme(m.from_user.id)
    if a[2] is None or '_' in m.data and a[2]:
        pid = False
    elif '_' in m.data and not a[2]:
        pid = True
    else:
        pid = a[2]
    pname = ['Texto', 'Telegra.ph']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=pname[pid], callback_data='pattern_')],
        [InlineKeyboardButton(text='Voltar', callback_data="settings")]
    ])
    db.def_theme(m.from_user.id, a[0], a[1], pid)
    await m.edit_message_text(
        'Escolha em baixo:', reply_markup=keyboard)
