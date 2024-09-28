from hydrogram import Client
from hydrogram.types import (
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from lyricspybot import database
from lyricspybot.locales import use_chat_lang
from lyricspybot.utils import musixmatch_client

# + original, - traduzido, _ telegraph


@Client.on_chosen_inline_result()
@use_chat_lang()
async def chosen(c: Client, m: ChosenInlineResult, t):
    if m.result_id == "MySpotify":
        return

    song_hash = m.result_id[1:] if m.result_id[0] in {"s", "l"} else m.result_id
    lyrics_data = await musixmatch_client.lyrics(song_hash)
    parsed_lyrics = musixmatch_client.parce(lyrics_data)
    user_id = m.from_user.id
    if database.theme(user_id)[2]:
        if parsed_lyrics["traducao"]:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{user_id}|{song_hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"_-{user_id}|{song_hash}"
                        ),
                    ]
                ]
            )
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("text"), callback_data=f"+{user_id}|{song_hash}"
                        )
                    ]
                ]
            )
        await c.edit_inline_text(
            m.inline_message_id,
            f'{parsed_lyrics["musica"]} - {parsed_lyrics["autor"]}\n{database.get_url(song_hash)[1]}',
            reply_markup=keyboard,
            parse_mode=None,
        )
    else:
        keyboard = (
            InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{user_id}|{song_hash}"
                        ),
                        InlineKeyboardButton(
                            text=t("port"), callback_data=f"-{user_id}|{song_hash}"
                        ),
                    ]
                ]
            )
            if parsed_lyrics["traducao"]
            else InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("tgph"), callback_data=f"_+{user_id}|{song_hash}"
                        )
                    ]
                ]
            )
        )
        database.add_hash(song_hash, parsed_lyrics)
        await c.edit_inline_text(
            m.inline_message_id,
            f"[{parsed_lyrics['musica']} - {parsed_lyrics['autor']}]({parsed_lyrics['link']})\n{parsed_lyrics['letra']}"[
                :4096
            ],
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
