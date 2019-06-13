import lyricspy
import threading
import markdown2
from config import bot
from telegraph import Telegraph
from amanobot.loop import MessageLoop
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup

telegraph = Telegraph()
telegraph.create_account(short_name='LyricsPyRobot', author_name='amn')


def send_te(a, b):
    response = telegraph.create_page(
        a['musica'],
        html_content='<a href="{}">{} - {}</a><br><br>{}'.format(a["link"], a["musica"], a["autor"],
                                                                 markdown2.markdown(b))
    )
    return response


def handle_thread(*args, **kwargs):
    t = threading.Thread(target=handle, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()


def handle(msg):
    if 'text' in msg:
        if msg['text'] == '/start':
            bot.sendMessage(msg['chat']['id'], f'Vai reclar no PV do @OLixao por isso não estar pronto',
                            reply_to_message_id=msg['message_id'])
        if msg['text'].startswith('/letra'):
            text = msg['text'][7:]
            if text == '':
                bot.sendMessage(msg['chat']['id'], 'uso:\n/letras nome da musica',
                                reply_to_message_id=msg['message_id'])
            else:
                a = lyricspy.auto(msg['text'][5:])[0]
                if not a:
                    bot.sendMessage(msg['chat']['id'], f'não existe resultado para {text}',
                                    reply_to_message_id=msg['message_id'])
                else:
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')]])
                    if a.get('traducao'):
                        teclado = InlineKeyboardMarkup(inline_keyboard=[
                            [dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')] +
                            [dict(text='Tradução', callback_data=f'tr_{a["link"]}|{msg["from"]["id"]}')]])
                    print(teclado)
                    bot.sendMessage(msg['chat']['id'],
                                    '[{} - {}]({})\n{}'.format(a["musica"], a["autor"], a['link'], a['letra']),
                                    reply_to_message_id=msg['message_id'], parse_mode='markdown',
                                    disable_web_page_preview=True, reply_markup=teclado)

    elif 'data' in msg:
        if 'tr_' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]):
                link = msg['data'][3:].split("|")[0]
                a = lyricspy.letra(link)
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Telegra.ph', callback_data=f'tell_{a["link"]}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell_{a["link"]}|{msg["from"]["id"]}')] +
                        [dict(text='Original', callback_data=f"tr-{a['link']}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'],
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['traducao']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['traducao']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
        if 'tell-' in msg['data']:
            print(msg)
            if msg["from"]["id"] == int(msg['data'].split('|')[1]):
                link = msg['data'][5:].split("|")[0]
                a = lyricspy.letra(link)
                response = send_te(a, a['letra'])
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Texto', callback_data=f"tr-{a['link']}|{int(msg['data'].split('|')[1])}")]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Texto', callback_data=f"tr-{a['link']}|{int(msg['data'].split('|')[1])}")] +
                        [dict(text='Traducão', callback_data=f"tell_{a['link']}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'], f'https://telegra.ph/{response["path"]}',
                                        reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        f'https://telegra.ph/{response["path"]}', reply_markup=teclado)
        if 'tell_' in msg['data']:
            print(msg)
            if msg["from"]["id"] == int(msg['data'].split('|')[1]):
                link = msg['data'][5:].split("|")[0]
                a = lyricspy.letra(link)
                response = send_te(a, a['traducao'])
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Texto', callback_data=f"tr_{a['link']}|{int(msg['data'].split('|')[1])}")]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Texto', callback_data=f"tr_{a['link']}|{int(msg['data'].split('|')[1])}")] +
                        [dict(text='Original', callback_data=f"tell-{a['link']}|{int(msg['data'].split('|')[1])}")]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'], f'https://telegra.ph/{response["path"]}',
                                        reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        f'https://telegra.ph/{response["path"]}', reply_markup=teclado)
        if 'tr-' in msg['data']:
            if msg["from"]["id"] == int(msg['data'].split('|')[1]):
                link = msg['data'][3:].split("|")[0]
                a = lyricspy.letra(link)
                teclado = InlineKeyboardMarkup(inline_keyboard=[
                    [dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')] +
                        [dict(text='Tradução', callback_data=f'tr_{a["link"]}|{msg["from"]["id"]}')]])
                if 'inline_message_id' in msg:
                    bot.editMessageText(msg['inline_message_id'],
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
                else:
                    bot.editMessageText((msg['message']['chat']['id'], msg['message']['message_id']),
                                        '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                        parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
    elif 'query' in msg:
        if msg.get('inline_message_id'):
            teclado = None
            try:
                a = lyricspy.letra(msg['result_id'])
                teclado = InlineKeyboardMarkup(
                    inline_keyboard=[[dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')]])
                if a.get('traducao'):
                    teclado = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Telegra.ph', callback_data=f'tell-{a["link"]}|{msg["from"]["id"]}')] +
                        [dict(text='Tradução', callback_data=f'tr_{a["link"]}|{msg["from"]["id"]}')]])
                    print(teclado)
                bot.editMessageText(msg['inline_message_id'],
                                    '[{} - {}]({})\n{}'.format(a['musica'], a['autor'], a['link'], a['letra']),
                                    parse_mode='markdown', disable_web_page_preview=True, reply_markup=teclado)
            except Exception as e:
                print(e)
                bot.editMessageText(msg['inline_message_id'], 'ocorreu um erro ao exibir a letra')
        elif msg['query'] != '':
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
            bot.answerInlineQuery(msg['id'], results=articles, is_personal=True)


print('LyricsPyRobot...')

MessageLoop(bot, handle_thread).run_forever()

while True:
    pass
