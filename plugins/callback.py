from config import bot
from lyricspy.aio import letras, muximatch
import db
import re

from amanobot.namedtuple import InlineKeyboardMarkup

#+ original, - traduzido, _ telegraph

mux = muximatch()
let = letras()

async def callback(msg):
    if msg['data'].startswith('_+'):
        user, hash = msg['data'][2:].split('|')
        n = db.get_url(hash)
        print(msg['data'][2:])
        if not n:
            await bot.answerCallbackQuery(msg['id'], text='Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            url = n[0]
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', url):
                a = await let.letra(url)
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', url):
                a = await mux.letra(url)
            else:
                await bot.answerCallbackQuery(msg['id'], text=f'link inválido:\n{url}', show_alert=True)
                return True
            print(a)
            if 'traducao' in a:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Texto', callback_data=f'+{user}|{hash}')]+[dict(text=a['tr_name']or'tradução', callback_data=f'_-{hash}')]])
            else:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Texto', callback_data=f'+{user}|{hash}')]])
            print(n)
            text = '{} - {}\n{}'.format(a["musica"], a["autor"], n[1])
            if 'inline_message_id' in msg:
                await bot.editMessageText(msg['inline_message_id'],
                                    text, reply_markup=teclado, parse_mode='markdown')
            else:
                await bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                    text, reply_markup=teclado, parse_mode='markdown')
    elif msg['data'].startswith('_-'):
        user, hash = msg['data'][2:].split('|')
        n = db.get_url(hash)
        print(msg['data'][2:])
        if not n:
            await bot.answerCallbackQuery(msg['id'], text='Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            url = n[0]
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', url):
                a = await let.letra(url)
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', url):
                a = await mux.letra(url)
            else:
                await bot.answerCallbackQuery(msg['id'], text=f'link inválido:\n{url}', show_alert=True)
                return True
            if 'traducao' in a:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Texto', callback_data=f'-{user}|{hash}')]+[dict(text='Original', callback_data=f'_+{hash}')]])
            else:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Texto', callback_data=f'-{user}|{hash}')]])
            text = '{} - {}\n{}'.format(a["musica"], a["autor"], n[2])
            if 'inline_message_id' in msg:
                await bot.editMessageText(msg['inline_message_id'],
                                    text, reply_markup=teclado, parse_mode='markdown')
            else:
                await bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                    text, reply_markup=teclado, parse_mode='markdown')
    elif msg['data'].startswith('+'):
        user, hash = msg['data'][1:].split('|')
        url = db.get_url(hash)
        print(msg['data'][2:])
        if not url:
            await bot.answerCallbackQuery(msg['id'], text='Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            url = url[0]
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', url):
                a = await let.letra(url)
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', url):
                a = await mux.letra(url)
            else:
                await bot.answerCallbackQuery(msg['id'], text=f'link inválido:\n{url}', show_alert=True)
                return True
            if 'traducao' in a:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]+[dict(text=a['tr_name']or'tradução', callback_data=f'-{hash}')]])
            else:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]])
            text = '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])
            if 'inline_message_id' in msg:
                await bot.editMessageText(msg['inline_message_id'],
                                    text, reply_markup=teclado, parse_mode='markdown', disable_web_page_preview=True)
            else:
                await bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                    text, reply_markup=teclado, parse_mode='markdown', disable_web_page_preview=True)
    elif msg['data'].startswith('-'):
        user, hash = msg['data'][1:].split('|')
        url = db.get_url(hash)
        print(msg['data'][2:])
        if not url:
            await bot.answerCallbackQuery(msg['id'], text='Hash não encontrado...\nEssa mensagem pode ser velha', show_alert=True)
        else:
            url = url[0]
            if re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', url):
                a = await let.letra(url)
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', url):
                a = await mux.letra(url)
            else:
                await bot.answerCallbackQuery(msg['id'], text=f'link inválido:\n{url}', show_alert=True)
                return True
            if 'traducao' in a:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_-{user}|{hash}')]+[dict(text='Original', callback_data=f'+{hash}')]])
            else:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_-{user}|{hash}')]])
            text = '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['traducao'])
            if 'inline_message_id' in msg:
                await bot.editMessageText(msg['inline_message_id'],
                                    text, reply_markup=teclado, parse_mode='markdown', disable_web_page_preview=True)
            else:
                await bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                    text, reply_markup=teclado, parse_mode='markdown', disable_web_page_preview=True)