from config import BOT_CONFIG
from db import db, dbc
from functools import partial

from pyromod.helpers import ikb
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Update
from locales import use_chat_lang
from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults
from pyrogram.raw.types import (
    DataJSON,
    InputMediaInvoice,
    Invoice,
    LabeledPrice,
    MessageActionPaymentSentMe,
    UpdateBotPrecheckoutQuery,
    UpdateNewMessage,
)

@Client.on_callback_query(filters.regex(r"donate"))
@use_chat_lang()
async def add_donate(c: Client, q:CallbackQuery, t):
    val = int(q.data.split("_")[1]) if "_" in q.data else 1000
    if val >= 650:
        key = [[
            ("+ R$ 1.00", f"donate_{val+100}"),
            ("+ R$ 0.50", f"donate_{val+50}"),
            ("R$ "+str(val/100), f"donation_{val}"),
            ("- R$ 0.50", f"donate_{val-50}"),
            ("- R$ 1.00", f"donate_{val-100}")
        ]]
        await q.edit_message_text(t("se_val"), reply_markup=ikb(key))

@Client.on_callback_query(filters.regex(r"donation"))
@use_chat_lang()
async def donate(c: Client, q:CallbackQuery, t):
    peer = await c.resolve_peer(q.from_user.id)
    await c.send(
        SendMedia(
            peer=peer,
            media=InputMediaInvoice(
                title=t("donation_title"),
                description=t("donation_desc"),
                invoice=Invoice(
                    currency="BRL",
                    # prices needs to be a list, even for a single item
                    prices=[LabeledPrice(label=t("donation_label"), amount=int(q.data.split("_")[1]))],
                    test=True,
                ),
                payload=b"payment",
                provider=BOT_CONFIG["STRIPE_TOKEN"],
                provider_data=DataJSON(data=r"{}"),
                start_param="pay",
            ),
            message="",
            random_id=c.rnd_id(),
        )
    )

@Client.on_raw_update(group=10)
async def raw_update(c: Client, update: Update, users: dict, chats: dict):
    if isinstance(update, UpdateBotPrecheckoutQuery):
        # This is to tell Telegram that everything is okay with this order.
        await c.send(SetBotPrecheckoutResults(query_id=update.query_id, success=True))

    if (
        isinstance(update, UpdateNewMessage)
        and hasattr(update.message, "action")
        and isinstance(update.message.action, MessageActionPaymentSentMe)
    ):
        # Sending a message confirming the order (additional to TGs service message)
        user = users[update.message.peer_id.user_id]
        await c.send_message(user.id, 'Order "confirmed".')
        print(user.id, user.first_name, "order confirmed")
        db.execute(
            "UPDATE users SET pro = ? WHERE user_id = ?", ("1", user.id)
        )
        db.commit()