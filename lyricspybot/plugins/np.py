"""
Now Playing Plugin for LyricsPyBot.

Displays currently playing songs from Spotify/Last.fm with playback controls,
lyrics search, and an approval system for viewing other users' status.
"""

import asyncio
import re
from contextlib import suppress
from datetime import datetime, timedelta

from hydrogram import Client, filters
from hydrogram.enums import ChatType, MessageEntityType
from hydrogram.enums.parse_mode import ParseMode
from hydrogram.errors import PeerIdInvalid, ReactionEmpty
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from spotipy.exceptions import SpotifyException

from lyricspybot import database
from lyricspybot.locales import use_chat_lang, use_user_lang
from lyricspybot.plugins.letra import get_lyrics
from lyricspybot.utils import (
    genius_client,
    get_current_track,
    get_song_art,
    get_spotify_session,
    get_track_info,
    http_client,
    musixmatch_client,
)

# Regular expression to extract Open Graph image from Last.fm pages
LASTFM_IMAGE_REGEX = re.compile(r"<meta property=\"og:image\" +?content=\"(.+)\"")


@Client.on_message(filters.command("np"))
@use_chat_lang()
async def now_playing(c: Client, m: Message, t):
    """
    Display currently playing song from Spotify or Last.fm.

    Supports checking other users' playback with approval system.
    Usage: /np [@user|user_id|reply]
    """
    # Parse command to check if user wants to see another user's now playing
    command_text = m.text.split(" ", 1)
    display_user_id = m.from_user.id
    if len(command_text) == 2:
        # Determine target user from various input methods
        if m.reply_to_message:
            # Get user from replied message
            target_user_id = m.reply_to_message.from_user.id
        elif m.entities and m.entities[0].type == MessageEntityType.TEXT_MENTION:
            # Get user from text mention (users without username)
            target_user_id = m.entities[0].user.id
        # User ids: integers
        elif m.command[1].isdigit():
            # Get user from numeric ID
            target_user_id = int(m.command[1])
        # Usernames and phone numbers with +
        else:
            # Get user from username or phone number
            target_user_id = m.command[1]
        target_user = await c.get_chat(target_user_id)
        approval_status = database.get_approved(target_user.id, m.from_user.id)

        # Only allow checking private chats (users), not groups
        if target_user.type != ChatType.PRIVATE:
            return await m.reply_text(t("only_users"))

        # Check if user has permission to view target's now playing
        if target_user.id == m.from_user.id or (
            approval_status and approval_status[0] == 1
        ):
            # User is checking themselves or has approval - increment usage count
            usage_count = approval_status[1] + 1 if approval_status[1] else 1
            database.add_approved(
                target_user.id,
                m.from_user.id,
                approval_status[0],
                usages=usage_count,
                usage=datetime.now().timestamp(),
            )
            display_user_id = m.from_user.id
            m.from_user.id = target_user.id
        elif approval_status and approval_status[0] == 0:
            # Request is pending approval
            return await m.reply_text(
                t("not_approved").format(first_name=target_user.first_name)
            )
        elif approval_status and approval_status[0] == 2:
            # User has been blocked by target
            return await m.reply_text(
                t("blocked").format(first_name=target_user.first_name)
            )
        else:
            # Send approval request to target user
            user_lang = use_user_lang(target_user.id)
            approval_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=user_lang("aprove"),
                            callback_data=f"aprova|{m.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text=user_lang("deny"),
                            callback_data=f"negar|{m.from_user.id}",
                        ),
                    ]
                ]
            )
            database.add_approved(
                target_user.id, m.from_user.id, False, dates=datetime.now().timestamp()
            )
            try:
                await c.send_message(
                    target_user.id,
                    user_lang("aprrovedu").format(name=m.from_user.first_name),
                    reply_markup=approval_keyboard,
                )
            except PeerIdInvalid:
                # Bot cannot send message to this user (never interacted or blocked)
                return await m.reply_text(
                    t("cant_send_request").format(name=target_user.first_name)
                )
            return await m.reply_text(
                t("approvedr").format(name=target_user.first_name)
            )

    # Try to get Spotify session for the user
    try:
        spotify_session = await get_spotify_session(m.from_user.id)
    except SpotifyException:
        spotify_session = None
    except (asyncio.TimeoutError, ConnectionError, OSError):
        return await m.reply_text(t("refresh_error"))

    # If no active Spotify playback, try Last.fm
    if not spotify_session or spotify_session.current_playback() is None:
        # Get Last.fm token from database
        user_token = database.get(m.from_user.id)
        if not user_token or not user_token[2]:
            return await m.reply_text(t("not_logged"))

        # Fetch currently scrobbling track from Last.fm
        current_track = await get_current_track(user_token[2])
        if not current_track:
            return await m.reply_text(t("not_playing"))

        # Get additional track information from Last.fm
        track_info = await get_track_info(
            user_token[2], current_track[0]["artist"]["#text"], current_track[0]["name"]
        )
        use_sticker = database.theme(display_user_id)[3]
        track_message = (
            f"🎵 {current_track[0]['artist']['#text']} - {current_track[0]['name']}"
        )

        # If user prefers text-only display, send as text
        if use_sticker is not None and not use_sticker:
            return await m.reply_text(
                track_message,
                parse_mode=ParseMode.HTML,
            )

        # Get album cover URL from Last.fm API
        album_cover_url = current_track[0]["image"][-1]["#text"]
        if not album_cover_url:
            # If not present in API return, scrape album URL from Last.fm page
            response = await http_client.get(
                current_track[0]["url"].replace("/_/", "/")
            )
            if response.status_code == 200:
                matches = LASTFM_IMAGE_REGEX.findall(response.text)
                album_cover_url = matches[0] if matches else None
            else:
                # Fallback to original URL if replacement fails
                fallback_response = await http_client.get(current_track[0]["url"])
                matches = LASTFM_IMAGE_REGEX.findall(fallback_response.text)
                album_cover_url = matches[0] if matches else None

        # Check if callback_data is within Telegram's 64 bytes limit
        artist_name = current_track[0]["artist"]["#text"]
        track_name = current_track[0]["name"]
        callback_data = f"lf_s|{artist_name}|{track_name}|{m.from_user.id}"
        keyb = None
        if len(callback_data.encode("utf-8")) <= 64:
            keyb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=t("search_lyric"),
                            callback_data=callback_data,
                        )
                    ]
                ]
            )

        if track_info.get("error"):
            return await m.reply_text(t("track_notfoud"))

        album_art = await get_song_art(
            song_name=current_track[0]["name"],
            artist_name=current_track[0]["artist"]["#text"],
            album_cover_url=album_cover_url,
            theme_color="dark" if database.theme(display_user_id)[0] else "light",
            blur_background=database.theme(display_user_id)[1],
            play_count=track_info["track"]["userplaycount"],
            source="lastfm",
        )
        return await m.reply_document(
            album_art, caption=track_message, reply_markup=keyb
        )

    # Handle Spotify playback
    spotify_data = spotify_session.current_playback(additional_types="episode,track")
    use_sticker = database.theme(display_user_id)[3]

    # Check if user is in private session
    if spotify_data["device"]["is_private_session"]:
        return await m.reply_text(t("private_session"))

    # Get artist name (handles both tracks and podcasts)
    if "artists" in spotify_data["item"]:
        artist_name = spotify_data["item"]["artists"][0]["name"]
    else:
        artist_name = spotify_data["item"]["show"]["name"]

    # Check if track is in user's favorites
    try:
        is_favorite = spotify_session.current_user_saved_tracks_contains([
            spotify_data["item"]["id"]
        ])[0]
    except SpotifyException:
        is_favorite = False

    # Generate album art with playback progress (if sticker mode enabled)
    if use_sticker is None or use_sticker:
        album_art = await get_song_art(
            song_name=spotify_data["item"]["name"],
            artist_name=artist_name,
            album_cover_url=spotify_data["item"]["album"]["images"][0]["url"]
            if "album" in spotify_data["item"]
            else spotify_data["item"]["images"][0]["url"],
            song_duration=spotify_data["item"]["duration_ms"] // 1000,
            playback_progress=spotify_data["progress_ms"] // 1000,
            theme_color="dark" if database.theme(display_user_id)[0] else "light",
            blur_background=database.theme(display_user_id)[1],
            source="spotify",
        )

    # Build track message and playback controls
    track_message = f"🎵 {artist_name} - {spotify_data['item']['name']}"
    playback_controls = [
        InlineKeyboardButton(text="⏮", callback_data=f"previous|{m.from_user.id}"),
        InlineKeyboardButton(
            text="⏸" if spotify_data["is_playing"] else "▶️",
            callback_data=f"pause|{m.from_user.id}"
            if spotify_data["is_playing"]
            else f"play|{m.from_user.id}",
        ),
        InlineKeyboardButton(text="⏭", callback_data=f"next|{m.from_user.id}"),
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            playback_controls,
            [
                InlineKeyboardButton(
                    text=t("play_in_sp"),
                    callback_data=f"tcs|{spotify_data['item']['id']}",
                ),
                InlineKeyboardButton(
                    text=t("search_lyric"),
                    callback_data=f"sp_s|{spotify_data['item']['id']}|{m.from_user.id}",
                ),
            ],
        ]
    )

    # Send response based on user's display preference
    if use_sticker is None or use_sticker:
        # Send as document with album art
        sent_message = await m.reply_document(
            album_art, reply_markup=keyboard, caption=track_message
        )
    else:
        # Send as text with device info and progress
        track_message = f"🎧 {spotify_data['item']['name']} - {artist_name}\n"
        track_message += (
            f"🗣 {spotify_data['device']['name']} | "
            f"⏳{timedelta(seconds=spotify_data['progress_ms'] // 1000)}"
        )
        sent_message = await m.reply_text(
            track_message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    # Add heart reaction if track is in favorites
    if is_favorite:
        await sent_message.react("❤")

    return True


@Client.on_callback_query(filters.regex(r"^aprova"))
@use_chat_lang()
async def approve(c: Client, m: CallbackQuery, t):
    """Approve a user's request to view now playing info."""
    user_id = m.data.split("|")[1]
    database.add_approved(
        m.from_user.id, user_id, True, dates=datetime.now().timestamp()
    )
    user = await c.get_users(user_id)
    user_lang = use_user_lang(user.id)
    await c.send_message(
        user_id, user_lang("approved").format(first_name=m.from_user.first_name)
    )
    await m.edit_message_text(t("sapproved").format(first_name=user.first_name))


@Client.on_callback_query(filters.regex(r"^negar"))
@use_chat_lang()
async def deny(c: Client, m: CallbackQuery, t):
    """Deny a user's request to view now playing info."""
    user_id = m.data.split("|")[1]
    database.add_approved(m.from_user.id, user_id, 2, dates=datetime.now().timestamp())
    user = await c.get_users(user_id)
    user_lang = use_user_lang(user.id)
    await c.send_message(
        user_id, user_lang("denied").format(first_name=m.from_user.first_name)
    )
    await m.edit_message_text(t("sdenied").format(first_name=user.first_name))


@Client.on_callback_query(filters.regex(r"^sp_s"))
@use_chat_lang()
async def spotify_search(c: Client, m: CallbackQuery, t):
    """Search and display lyrics for the current Spotify track."""
    track, user_id = m.data.split("|")[1:]
    # Ensure only the original requester can trigger lyrics search
    if m.from_user.id != int(user_id):
        return

    spotify_session = await get_spotify_session(m.from_user.id)
    original_message = m.message
    original_message.from_user = m.from_user
    spotify_track = spotify_session.track(track)

    # Try Genius first for lyrics
    genius_lyrics = await genius_client.spotify_lyrics(
        artist=spotify_track["artists"][0]["name"],
        track=spotify_track["name"],
    )
    if genius_lyrics:
        original_message.text = "/letra genius:" + str(genius_lyrics)
    else:
        # Fallback to Musixmatch if Genius fails
        lyrics_data = await musixmatch_client.spotify_lyrics(
            artist=spotify_track["artists"][0]["name"],
            track=spotify_track["name"],
        )
        if lyrics_data:
            original_message.text = "/letra musixmatch:" + str(
                lyrics_data["message"]["body"]["macro_calls"]["matcher.track.get"][
                    "message"
                ]["body"]["track"]["track_id"]
            )
        else:
            await original_message.reply_text(t("lyrics_nf", context="letra"))
            return

    await get_lyrics(c, original_message, t)
    return


@Client.on_callback_query(filters.regex(r"^lf_s"))
@use_chat_lang()
async def lastfm_search(c: Client, m: CallbackQuery, t):
    """Search and display lyrics for the current Last.fm track."""
    artist, track, user_id = m.data.split("|")[1:]
    print(artist, track, user_id)
    # Ensure only the original requester can trigger lyrics search
    if m.from_user.id != int(user_id):
        return

    original_message = m.message
    original_message.from_user = m.from_user

    # Try Genius first for lyrics
    genius_lyrics = await genius_client.spotify_lyrics(artist=artist, track=track)
    if genius_lyrics:
        original_message.text = "/letra genius:" + str(genius_lyrics)
        print(original_message.text)
    else:
        # Fallback to Musixmatch if Genius fails
        lyrics_data = await musixmatch_client.lyrics(f"{artist} {track}")
        if lyrics_data:
            original_message.text = "/letra musixmatch:" + str(
                lyrics_data["message"]["body"]["macro_calls"]["matcher.track.get"][
                    "message"
                ]["body"]["track"]["track_id"]
            )
        else:
            await original_message.reply_text(t("lyrics_nf", context="letra"))
            return

    await get_lyrics(c, original_message, t)


@Client.on_callback_query(filters.regex(r"^tcs"))
@use_chat_lang()
async def add_to_queue(_: Client, m: CallbackQuery, t):
    """Add the current Spotify track to user's queue."""
    spotify_session = await get_spotify_session(m.from_user.id)
    spotify_session.add_to_queue(uri=f"spotify:track:{m.data.split('|')[1]}")
    await m.answer(t("song_added"))


@Client.on_callback_query(filters.regex(r"^(pause|play|next|previous)"))
@use_chat_lang()
async def update_playback_info(c: Client, m: CallbackQuery, t):
    """Handle Spotify playback controls and update display."""
    action, user_id = m.data.split("|")
    # Verify the requester is the owner of the playback session
    if m.from_user.id != int(user_id):
        user = await c.get_chat(int(user_id))
        await m.answer(t("not_allowed").format(first_name=user.first_name))
        return

    spotify_session = await get_spotify_session(m.from_user.id)
    devices = spotify_session.devices()
    # Find the currently active device
    active_device = next(
        (device for device in devices["devices"] if device["is_active"]), None
    )
    if not active_device:
        return

    device_id = active_device["id"]

    # Execute the requested playback action
    if action == "previous":
        spotify_session.previous_track(device_id)
    elif action == "next":
        spotify_session.next_track(device_id)
    elif action == "pause":
        spotify_session.pause_playback(device_id)
    elif action == "play":
        spotify_session.start_playback(device_id)

    asyncio.sleep(1)  # Wait for Spotify to update playback state
    spotify_data = spotify_session.current_playback(additional_types="episode,track")

    # Rebuild keyboard with updated play/pause button
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏮", callback_data=f"previous|{m.from_user.id}"
                ),
                InlineKeyboardButton(
                    text="⏸" if spotify_data["is_playing"] else "▶️",
                    callback_data=f"pause|{m.from_user.id}"
                    if spotify_data["is_playing"]
                    else f"play|{m.from_user.id}",
                ),
                InlineKeyboardButton(text="⏭", callback_data=f"next|{m.from_user.id}"),
            ],
            [
                InlineKeyboardButton(
                    text=t("play_in_sp"),
                    callback_data=f"tcs|{spotify_data['item']['id']}",
                ),
                InlineKeyboardButton(
                    text=t("search_lyric"),
                    callback_data=f"sp_s|{spotify_data['item']['id']}|{m.from_user.id}",
                ),
            ],
        ]
    )

    # Get artist name (handles both tracks and podcasts)
    if "artists" in spotify_data["item"]:
        artist_name = spotify_data["item"]["artists"][0]["name"]
    else:
        artist_name = spotify_data["item"]["show"]["name"]

    # Check if track is in user's favorites
    try:
        is_favorite = spotify_session.current_user_saved_tracks_contains([
            spotify_data["item"]["id"]
        ])[0]
    except SpotifyException:
        is_favorite = False

    # Update heart reaction based on favorite status
    with suppress(ReactionEmpty):
        await m.message.react("❤" if is_favorite else "")

    # Update message display based on user preference
    if not database.theme(m.from_user.id)[3]:
        # Text-only mode: Update message text with new playback info
        track_message = f"🎧 {spotify_data['item']['name']} - {artist_name}\n"
        progress = timedelta(seconds=spotify_data["progress_ms"] // 1000)
        track_message += f"🗣 {spotify_data['device']['name']} | ⏳{progress}"
        await m.edit_message_text(
            track_message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        # Sticker mode: Show popup with track info and update keyboard only
        await m.answer(f"🎵 {artist_name} - {spotify_data['item']['name']}")
        if action in {"pause", "play"}:
            await m.edit_message_reply_markup(reply_markup=keyboard)
