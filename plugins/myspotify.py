from pyrogram import Client, filters
from pyromod.helpers import ikb
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

import asyncio
import db
import datetime
from utils import get_spoti_session
from locales import use_chat_lang

@Client.on_inline_query(filters.regex(r"^my"), group=0)
@use_chat_lang()
async def my_spotify(c, m, t):
    tk = db.get(m.from_user.id)
    if tk and tk[0]:
        sess = await get_spoti_session(m.from_user.id)
        spotify_json = sess.current_playback(additional_types="episode,track")
        if not spotify_json:
            article = [InlineQueryResultArticle(
                title=t("my_spotify"),
                description=t("no_playng"),
                id="MySpotify",
                thumb_url="https://piics.ml/amn/lpy/spoti.png",
                input_message_content=InputTextMessageContent(
                message_text=t("play"),
                ),
            )]
            return await m.answer(article, cache_time=0)
        if spotify_json["repeat_state"] == "track":
            emoji = '🔂'
            call = f'sploopt|{m.from_user.id}'
        elif spotify_json["repeat_state"] == 'context':
            emoji = '🔁'
            call = f'sploopc|{m.from_user.id}'
        else:
            emoji = '↪️'
            call = f'sploopo|{m.from_user.id}'
        if "artists" in spotify_json["item"]:
            publi = spotify_json["item"]["artists"][0]["name"]
        else:
            publi = spotify_json["item"]["show"]["name"]
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton('⏮', f'spprevious|{m.from_user.id}')]+
                [InlineKeyboardButton('⏸' if spotify_json["is_playing"] else "▶️",
                f"sppause|{m.from_user.id}" if spotify_json["is_playing"] else f"spplay|{m.from_user.id}")]+
                [InlineKeyboardButton('⏭', f"spnext|{m.from_user.id}")]+
                [InlineKeyboardButton(emoji, call)],
                [InlineKeyboardButton(f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')],
                [InlineKeyboardButton(t('top_button'), f'top|{m.from_user.id}')]+
                [InlineKeyboardButton(t('recent_button'), f'recently|{m.from_user.id}')],
            ]
        )
        text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
        text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'
        
        article = [InlineQueryResultArticle(
            title=t("my_spotify"),
            description=f'🎧 {spotify_json["item"]["name"]} - {publi}',
            id="MySpotify",
            thumb_url="https://piics.ml/amn/lpy/spoti.png",
            reply_markup=keyboard,
            input_message_content=InputTextMessageContent(
                message_text=(text),
            ),
        )]
        return await m.answer(article, cache_time=0)

#Player
@Client.on_callback_query(filters.regex("^spprevious"))
@use_chat_lang()
async def previous(c: Client, m, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        return await m.answer(t("not_allowed").format(first_name=m.from_user.first_name))
    sp = await get_spoti_session(m.from_user.id)
    if not 'premium' in sp.current_user()["product"]:
        return await m.answer(t("premium_only"))
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            device_name = i["name"]
            break
    sp.previous_track(device_id)
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    
    if spotify_json["repeat_state"] == "track":
        emoji = '🔂'
        call = f'sploopt|{m.from_user.id}'
    elif spotify_json["repeat_state"] == 'context':
        emoji = '🔁'
        call = f'sploopc|{m.from_user.id}'
    else:
        emoji = '↪️'
        call = f'sploopo|{m.from_user.id}'
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ('⏮', f'spprevious|{m.from_user.id}'),
            ('⏸' if spotify_json["is_playing"] else "▶️",
             f'sppause|{m.from_user.id}' if spotify_json["is_playing"] else f"spplay|{m.from_user.id}"),
            ('⏭', f'spnext|{m.from_user.id}'),
            (emoji, call)
        ],
        [
            (f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')
        ],
        [
            (t('top_button'), f'top|{m.from_user.id}'),
            (t('recent_button'), f'recently|{m.from_user.id}')
        ]
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex("^spnext"))
@use_chat_lang()
async def next(c: Client, m, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        return await m.answer(t("not_allowed").format(first_name=m.from_user.first_name))
    sp = await get_spoti_session(m.from_user.id)
    if not 'premium' in sp.current_user()["product"]:
        return await m.answer(t("premium_only"))
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            device_name = i["name"]
            break
    sp.next_track(device_id)
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    
    if spotify_json["repeat_state"] == "track":
        emoji = '🔂'
        call = f'sploopt|{m.from_user.id}'
    elif spotify_json["repeat_state"] == 'context':
        emoji = '🔁'
        call = f'sploopc|{m.from_user.id}'
    else:
        emoji = '↪️'
        call = f'sploopo|{m.from_user.id}'
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ('⏮', f'spprevious|{m.from_user.id}'),
            ('⏸' if spotify_json["is_playing"] else "▶️",
             f'sppause|{m.from_user.id}' if spotify_json["is_playing"] else f"spplay|{m.from_user.id}"),
            ('⏭', f'spnext|{m.from_user.id}'),
            (emoji, call)
        ],
        [
            (f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')
        ],
        [
            (t('top_button'), f'top|{m.from_user.id}'),
            (t('recent_button'), f'recently|{m.from_user.id}')
        ]
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))

@Client.on_callback_query(group=1)
async def aa(c, m):
    print(m.data)

@Client.on_callback_query(filters.regex("^sploopo|sploopc|sploopt"))
@use_chat_lang()
async def pauseplay(c: Client, m, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        return await m.answer(t("not_allowed").format(first_name=m.from_user.first_name))
    sp = await get_spoti_session(m.from_user.id)
    if not 'premium' in sp.current_user()["product"]:
        return await m.answer(t("premium_only"))
    spotify_json = sp.current_playback(additional_types="episode,track")
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            device_name = i["name"]
            break
    if spotify_json["repeat_state"] == 'context':
        sp.repeat('track',device_id)
        emoji = '🔂'
        callb = f'sploopt|{m.from_user.id}'
    elif spotify_json["repeat_state"] == 'off':
        sp.repeat('context', device_id)
        emoji = '🔁'
        callb = f'sploopc|{m.from_user.id}'
    else:
        sp.repeat('off',device_id)
        emoji = '↪️'
        callb = f'sploopo|{m.from_user.id}'
    await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ('⏮', f'spprevious|{m.from_user.id}'),
            ('⏸' if spotify_json["is_playing"] else "▶️",
             f'sppause|{m.from_user.id}' if spotify_json["is_playing"] else f"spplay|{m.from_user.id}"),
            ('⏭', f'spnext|{m.from_user.id}'),
            (emoji, callb)
        ],
        [
            (f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')
        ],
        [
            (t('top_button'), f'top|{m.from_user.id}'),
            (t('recent_button'), f'recently|{m.from_user.id}')
        ]
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex('^recently|top'))
@use_chat_lang()
async def recently(c: Client, m, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        return await m.answer(t("not_allowed").format(first_name=m.from_user.first_name))
    sp = await get_spoti_session(m.from_user.id)
    profile = sp.current_user()
    if m.data.split("|")[0] == "recently":
        text = t('recent_text').format(name=profile["display_name"])
        li = sp.current_user_recently_played(limit=10)
    else:
        text = t('top_text').format(name=profile["display_name"])
        li = sp.current_user_top_tracks(limit=10)
    for n, i in enumerate(li["items"]):
        res = i["track"] if "track" in i else i
        text += f'{n+1}. {res["artists"][0]["name"]} - {res["name"]}\n'
    
    
    spotify_json = sp.current_playback(additional_types="episode,track")
        
    if spotify_json["repeat_state"] == "track":
        emoji = '🔂'
        call = f'sploopt|{m.from_user.id}'
    elif spotify_json["repeat_state"] == 'context':
        emoji = '🔁'
        call = f'sploopc|{m.from_user.id}'
    else:
        emoji = '↪️'
        call = f'sploopo|{m.from_user.id}'
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ('⏮', f'spprevious|{m.from_user.id}'),
            ('⏸' if spotify_json["is_playing"] else "▶️",
             f'sppause|{m.from_user.id}' if spotify_json["is_playing"] else f"spplay|{m.from_user.id}"),
            ('⏭', f'spnext|{m.from_user.id}'),
            (emoji, call)
        ],
        [
            (f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')
        ],
        [
            (t('top_button'), f'top|{m.from_user.id}'),
            (t('recent_button'), f'recently|{m.from_user.id}')
        ]
    ]
    await m.edit_message_text(text, reply_markup=ikb(keyb))

@Client.on_callback_query(filters.regex("^sppause|^spplay|^spmain"))
@use_chat_lang()
async def pauseplay(c: Client, m, t):
    if m.data.split("|")[1] != str(m.from_user.id):
        sess = await get_spoti_session(m.from_user.id)
        sess.add_to_queue(uri=f'spotify:track:{m.data.split("|")[2]}')
        return await m.answer(t("song_added"))
    sp = await get_spoti_session(m.from_user.id)
    if not 'premium' in sp.current_user()["product"]:
        return await m.answer(t("not_premium"))
    devices = sp.devices()
    for i in devices["devices"]:
        if i["is_active"]:
            device_id = i["id"]
            device_name = i["name"]
            break
    spotify_json = sp.current_playback(additional_types="episode,track")
    if m.data.split("|")[0] != "spmain":
        if spotify_json["is_playing"]:
            sp.pause_playback(device_id)
        else:
            sp.start_playback(device_id)
        await asyncio.sleep(0.5)
    spotify_json = sp.current_playback(additional_types="episode,track")
        
    if spotify_json["repeat_state"] == "track":
        emoji = '🔂'
        call = f'sploopt|{m.from_user.id}'
    elif spotify_json["repeat_state"] == 'context':
        emoji = '🔁'
        call = f'sploopc|{m.from_user.id}'
    else:
        emoji = '↪️'
        call = f'sploopo|{m.from_user.id}'
    if "artists" in spotify_json["item"]:
        publi = spotify_json["item"]["artists"][0]["name"]
    else:
        publi = spotify_json["item"]["show"]["name"]
    keyb = [
        [
            ('⏮', f'spprevious|{m.from_user.id}'),
            ('⏸' if spotify_json["is_playing"] else "▶️",
             f'sppause|{m.from_user.id}' if spotify_json["is_playing"] else f"spplay|{m.from_user.id}"),
            ('⏭', f'spnext|{m.from_user.id}'),
            (emoji, call)
        ],
        [
            (f'{spotify_json["item"]["name"]} - {publi}', f'spmain|{m.from_user.id}|{spotify_json["item"]["id"]}')
        ],
        [
            (t('top_button'), f'top|{m.from_user.id}'),
            (t('recent_button'), f'recently|{m.from_user.id}')
        ]
    ]
    text = f'🎧 {spotify_json["item"]["name"]} - {publi}\n'
    text += f'🗣 {spotify_json["device"]["name"]} | ⏳{datetime.timedelta(seconds=spotify_json["progress_ms"] // 1000)}'

    await m.edit_message_text(text, reply_markup=ikb(keyb))