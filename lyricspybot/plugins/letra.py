import re

from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from lyricspybot import database
from lyricspybot.locales import use_chat_lang
from lyricspybot.utils import genius_client, musixmatch_client

# + original, - translated, _ telegraph


@Client.on_message(filters.command(["lyrics", "letra"]))
@use_chat_lang()
async def get_lyrics(c: Client, m: Message, t):
    """
    Searches and displays the lyrics of the song provided by the user.
    """
    print(m)
    if not m.text or len(m.text.split(" ", 1)) < 2:
        await m.reply_text(t("use"))
        return
    query = m.text.split(" ", 1)[1].strip()
    if not query:
        await m.reply_text(t("use"))
        return
    elif "musixmatch:" in query:
        lyrics_data = await musixmatch_client.auto(id=query.split(":", 1)[1])
    elif "genius:" in query:
        lyrics_data = await genius_client.lyrics(query.split(":", 1)[1])
    elif re.match(
        r"^(https?://)?(letras\.mus.br/|(m\.|www\.)?letras\.mus\.br/).+", query
    ):
        lyrics_data = await genius_client.auto(query)
    elif re.match(
        r"^(https?://)?(musixmatch\.com/|(m\.|www\.)?musixmatch\.com/).+", query
    ):
        lyrics_data = await musixmatch_client.lyrics(query)
    else:
        lyrics_data = await genius_client.auto(query, limit=1)
        if not lyrics_data:
            lyrics_data = await musixmatch_client.auto(q=query, limit=1)
        if not lyrics_data:
            await m.reply_text(t("lyrics_nf"))
            return
    lyrics_data = lyrics_data[0] if isinstance(lyrics_data, list) else lyrics_data
    print(lyrics_data)
    lyrics_data = (
        genius_client.parse(lyrics_data)
        if "meta" in lyrics_data
        else musixmatch_client.parce(lyrics_data)
    )
    print(lyrics_data)
    lyrics_hash = str(lyrics_data["id"])
    database.add_hash(lyrics_hash, lyrics_data)
    user_id = m.from_user.id
    if database.theme(m.from_user.id)[2]:
        if lyrics_data["traducao"]:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{user_id}|{lyrics_hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"_-{user_id}|{lyrics_hash}"
                        ),
                    ]
                ]
            )
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{user_id}|{lyrics_hash}"
                        )
                    ]
                ]
            )
        await m.reply_text(
            f'{lyrics_data["musica"]} - {lyrics_data["autor"]}\n{database.get_url(lyrics_hash)[1]}',
            reply_markup=keyboard,
            parse_mode=None,
        )
    else:
        keyboard = (
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{user_id}|{lyrics_hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"-{user_id}|{lyrics_hash}"
                        ),
                    ]
                ]
            )
            if lyrics_data["traducao"]
            else InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{user_id}|{lyrics_hash}"
                        )
                    ]
                ]
            )
        )
        await m.reply_text(
            f"[{lyrics_data['musica']} - {lyrics_data['autor']}]({lyrics_data['link']})\n{lyrics_data['letra']}"[
                :4096
            ],
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    return
