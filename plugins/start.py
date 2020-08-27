from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("start"))
async def start(c, m):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Pesquisar letra', switch_inline_query_current_chat='')]
    ])
    await m.reply_text('Pesquise por letras de músicas direto do Telegram :D\n\n'
                          '   - __Para mais informaçoes, use__ /help\n\n'
                          'Vamos iniciar? Comece testando pelo botão abaixo:', reply_markup=keyboard)

@Client.on_message(filters.command("help"))
async def help(c, m):
    await m.reply_text('Este bot exibe letra de músicas de acordo com sua pesquisa, utilizando o musixmatch.com.\n\n'
                          'Você pode pesquisar atravez do modo inline (@lyricspyrobot <música>), ou até mesmo ver a letra da música que está tocando em seu Spotify atravez do spoti (necessitalogin) :D\n\n'
                          'Os seguintes comandos estão disponiveis:\n'
                          '   • /letra <música> (pesquisa determinada letra)\n'
                          '   • /spoti (mostra a música atual tocando ~não necessita premium~)\n\n'
                          'Em caso de dúvida, entre em contato pelo @AmanoSupport ou por nosso chat @AmanoChat.\n'
                          '- Novidades e atualizações serão postadas no canal @AmanoTeam.')