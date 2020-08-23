from config import bot
from amanobot.namedtuple import InlineKeyboardMarkup
from lyricspy.aio import letras, muximatch
import re
import hashlib
from plugins.spoti import spoti
from plugins.lastfm import lastfm
import db

mux = muximatch()
let = letras()

async def handle(msg):
    if msg.get('text'):
        if msg['text'] == '/start':
            teclado = InlineKeyboardMarkup(
                inline_keyboard=[[dict(text='Pesquisar letras', switch_inline_query_current_chat='')]])
            await bot.sendMessage(msg['chat']['id'],
                            'Pesquise por letras de músicas direto do Telegram :D\n\n'
                            '   - _Para mais informaçoes, use_ /help\n\n'
                            'Vamos iniciar? Comece testando pelo botão abaixo:',
                            reply_to_message_id=msg['message_id'],
                            reply_markup=teclado,
                            parse_mode='markdown')
        elif msg['text'] == '/help':
            await bot.sendMessage(msg['chat']['id'],
                            'Este bot exibe letra de músicas de acordo com sua pesquisa, utilizando o musixmatch.com.\n\n'
                            'Você pode pesquisar atravez do modo inline (@lyricspyrobot <música>), ou até mesmo ver a letra da música que está tocando em seu Spotify atravez do spoti (necessitalogin) :D\n\n'
                            'Os seguintes comandos estão disponiveis:\n'
                            '   • /letra <música> (pesquisa determinada letra)\n'
                            '   • /spoti (mostra a música atual tocando ~não necessita premium~)\n\n'
                            'Em caso de dúvida, entre em contato pelo @AmanoSupport ou por nosso chat @AmanoChat.\n'
                            '- Novidades e atualizações serão postadas no canal @AmanoTeam.',reply_to_message_id=msg['message_id'])
        elif msg['text'].startswith('/letra'):
            text = msg['text'].split(' ', 1)[1]
            if not text:
                await bot.sendMessage(msg['chat']['id'],
                            '**Uso:** /letra <nome da música>',reply_to_message_id=msg['message_id'])
            elif re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', text):
                a = await let.letra(text)
            elif re.match(r'^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+', text):
                a = await mux.letra(text)
            else:
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
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]+[dict(text=a['tr_name']or'tradução', callback_data=f'-{user}|{hash}')]])
            else:
                teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'_+{user}|{hash}')]])
            await bot.sendMessage(msg['chat']['id'],
                            '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra'])[:4096]
                            ,reply_to_message_id=msg['message_id'], disable_web_page_preview=True, reply_markup=teclado,parse_mode='markdown')
        elif msg['text'].startswith('/spoti'):
            await spoti(msg)
        elif msg['text'].startswith('/lfm'):
            await lastfm(msg)