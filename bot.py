import lyricspy
import threading
import markdown2
from config import bot,sudos
from telegraph import Telegraph
from amanobot.loop import MessageLoop
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup
import re
from db import dbc
from spoti import spoti, inline

telegraph = Telegraph()
telegraph.create_account(short_name='LyricsPyRobot', author_name='amn')


def send_te(a, b):
    response = telegraph.create_page(
        a['musica'],
        html_content=markdown2.markdown(b.replace('\n','<br>')),
        author_name=a["autor"],
        author_url=a["link"]
    )
    return response


def handle_thread(*args, **kwargs):
    t = threading.Thread(target=handle, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()


def handle(msg):
    if 'text' in msg:
        if '/spoti' in msg['text']:
            spoti(msg,bot)
        elif msg['text'] == '/start':
            teclado = InlineKeyboardMarkup(inline_keyboard=[[dict(text='Pesquisar letras', switch_inline_query_current_chat='')]])
            bot.sendMessage(msg['chat']['id'], f'Pesquise por letras de músicas direto do telegram\n\nTeste apertando o botão abaixo:',
                            reply_to_message_id=msg['message_id'],
                            reply_markup=teclado)
        elif msg['text'].split()[0] == '/letras':
            text = msg['text'].split()[1]
            if text == '':
                bot.sendMessage(msg['chat']['id'], 'uso:\n/letras nome da musica',
                                reply_to_message_id=msg['message_id'])
            else:
                res = ['{}: <a href="{}">{} - {}</a>'.format(num+1, i['link'], i["musica"], i["autor"]) for num, i in enumerate(lyricspy.auto(text,30))] or "Nenhum resultado foi encontrado"
                bot.sendMessage(msg['chat']['id'], '\n'.join(res), 'HTML',reply_to_message_id=msg['message_id'],disable_web_page_preview=True)
        elif msg['text'].split()[0] == '/letra':
            text = msg['text'][7:]
            if text == '':
                bot.sendMessage(msg['chat']['id'], 'uso:\n/letra nome ou url da letra',
                                reply_to_message_id=msg['message_id'])
            elif re.match(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+', text):
                a = lyricspy.letra(text)
                if a:
                    mik = re.split(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br)', a["link"])[-1]
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')]])
                    if a.get('traducao'):
                        teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')] +
                            [dict(text='Tradução', callback_data=f'tr_{mik}|{msg["from"]["id"]}')]])
                    bot.sendMessage(msg['chat']['id'],
                                    '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra']),
                                    reply_to_message_id=msg['message_id'], parse_mode='markdown',
                                    disable_web_page_preview=True, reply_markup=teclado) 
            else:
                a = lyricspy.auto(text)[0]
                if a.get('letra'):
                    mik = re.split(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br)', a["link"])[-1]
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')]])
                    if a.get('traducao'):
                        teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')] +
                            [dict(text='Tradução', callback_data=f'tr_{mik}|{msg["from"]["id"]}')]])
                    bot.sendMessage(msg['chat']['id'],
                                    '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra']),
                                    reply_to_message_id=msg['message_id'], parse_mode='markdown',
                                    disable_web_page_preview=True, reply_markup=teclado) 

    elif 'data' in msg:
        if 'tr_' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]) or msg["from"]["id"] in sudos:
                link = msg['data'][3:].split("|")[0]
                a = lyricspy.letra('https://m.letras.mus.br'+link)
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Telegra.ph', callback_data=f'tell_{link}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell_{link}|{msg["from"]["id"]}')] +
                        [dict(text='Original', callback_data=f"tr-{link}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'],
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['traducao']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['traducao']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
            else:
                bot.answerCallbackQuery(msg['id'], text='Você não pode editar esta mensagem',show_alert=True)
        if 'tell-' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]) or msg["from"]["id"] in sudos:
                link = msg['data'][5:].split("|")[0]
                a = lyricspy.letra('https://m.letras.mus.br'+link)
                response = send_te(a, a['letra'])
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Texto', callback_data=f"tr-{link}|{int(msg['data'].split('|')[1])}")]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Texto', callback_data=f"tr-{link}|{int(msg['data'].split('|')[1])}")] +
                        [dict(text='Traducão', callback_data=f"tell_{link}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'], f'https://telegra.ph/{response["path"]}',
                                        reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        f'https://telegra.ph/{response["path"]}', reply_markup=teclado)
            else:
                bot.answerCallbackQuery(msg['id'], text='Você não pode editar esta mensagem',show_alert=True)
        if 'tell_' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]) or msg["from"]["id"] in sudos:
                link =  msg['data'][5:].split("|")[0]
                a = lyricspy.letra('https://m.letras.mus.br'+link)
                response = send_te(a, a['traducao'])
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Texto', callback_data=f"tr_{link}|{int(msg['data'].split('|')[1])}")]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Texto', callback_data=f"tr_{link}|{int(msg['data'].split('|')[1])}")] +
                        [dict(text='Original', callback_data=f"tell-{link}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'], f'https://telegra.ph/{response["path"]}',
                                        reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        f'https://telegra.ph/{response["path"]}', reply_markup=teclado)
            else:
                bot.answerCallbackQuery(msg['id'], text='Você não pode editar esta mensagem',show_alert=True)
        if 'tr-' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]) or msg["from"]["id"] in sudos:
                link = msg['data'][3:].split("|")[0]
                a = lyricspy.letra('https://m.letras.mus.br'+link)
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Telegra.ph', callback_data=f'tell-{link}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell-{link}|{msg["from"]["id"]}')] +
                        [dict(text='Tradução', callback_data=f'tr_{link}|{msg["from"]["id"]}')]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'],
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
            else:
                bot.answerCallbackQuery(msg['id'], text='Você não pode editar esta mensagem',show_alert=True)
    elif 'query' in msg:
        if msg.get('inline_message_id'):
            teclado = None
            try:
                a = lyricspy.letra(msg['result_id'])
                mik = re.split(r'^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br)', a["link"])[-1]
                teclado = InlineKeyboardMarkup(
                    inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell-{mik}|{msg["from"]["id"]}')] +
                        [dict(text='Tradução', callback_data=f'tr_{mik}|{msg["from"]["id"]}')]])
                print(teclado)
                try:
                    bot.editMessageText(msg['inline_message_id'],
                                    '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                    parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
                except:
                    bot.editMessageText(msg['inline_message_id'],
                                    '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                    parse_mode='markdown', disable_web_page_preview=True)
            except Exception as e:
                print(e)
                bot.editMessageText(msg['inline_message_id'], f'ocorreu um erro ao exibir a letra\nErro:{e}')
        elif msg['query'] == '':
            db = dbc()
            if str(msg['from']['id']) in db:
                articles = inline(msg, bot)
            else:
                articles = []
            bot.answerInlineQuery(msg['id'], results=articles, is_personal=True, cache_time=0)
        elif msg['query'] != '':
            db = dbc()
            if str(msg['from']['id']) in db:
                articles = inline(msg, bot)
                resy = articles
            else:
                articles = []
            result = lyricspy.auto(msg['query'])
            for a in result:
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Aguarde...', callback_data='a')]
                ])
                articles.append(InlineQueryResultArticle(
                    id=a['link'],
                    title=f'{a["musica"]} - {a["autor"]}',
                    input_message_content=InputTextMessageContent(
                        message_text='Aguarde...',
                        parse_mode='markdown', disable_web_page_preview=True),
                    reply_markup=teclado)
                )
            if not articles:
                articles = [InlineQueryResultArticle(id='abcde', title=f'sem resultado',
                                                     input_message_content=InputTextMessageContent(
                                                         message_text=f"sem resultado para {msg['query']}"))]
            try:
                bot.answerInlineQuery(msg['id'], results=articles, is_personal=True, cache_time=0)
            except:
                if resy:
                    bot.answerInlineQuery(msg['id'], results=resy, is_personal=True, cache_time=0)


print('LyricsPyRobot...')

MessageLoop(bot, handle_thread).run_forever()

while True:
    pass
