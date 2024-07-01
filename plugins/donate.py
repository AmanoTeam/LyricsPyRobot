from typing import Union

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults
from hydrogram.raw.types import (
    DataJSON,
    InputMediaInvoice,
    Invoice,
    LabeledPrice,
    MessageActionPaymentSentMe,
    UpdateBotPrecheckoutQuery,
    UpdateNewMessage,
)
from hydrogram.types import CallbackQuery, Message, Update

from config import stripe_token, sudos
from locales import use_chat_lang, use_user_lang


@Client.on_callback_query(filters.regex(r"donate"))
@use_chat_lang()
async def add_donate(c: Client, q: CallbackQuery, t):
    val = int(q.data.split("_")[1]) if "_" in q.data else 1000
    if val >= 650:
        key = [
            [
                ("+ R$ 100,00", f"donate_{val+10000}"),
                ("+ R$ 10,00", f"donate_{val+1000}"),
                ("+ R$ 1,00", f"donate_{val+100}"),
                ("+ R$ 0,50", f"donate_{val+50}"),
            ],
            [(f"R$ {str(val / 100)}", f"donation_{val}")],
            [
                ("- R$ 100,00", f"donate_{val-10000}"),
                ("- R$ 10,00", f"donate_{val-1000}"),
                ("- R$ 1,00", f"donate_{val-100}"),
                ("- R$ 0,50", f"donate_{val-50}"),
            ],
        ]

        await q.edit_message_text(t("se_val"), reply_markup=ikb(key))


@Client.on_message(filters.regex(r"\/start pay"))
@Client.on_callback_query(filters.regex(r"donation"))
@use_chat_lang()
async def donation(c: Client, q: Union[CallbackQuery, Message], t):
    peer = await c.resolve_peer(q.from_user.id)
    val = (
        int(q.data.split("_")[1])
        if isinstance(q, CallbackQuery)
        else int(q.text.split("_")[1])
    )
    key = stripe_token["TEST"] if q.from_user.id in sudos else stripe_token["LIVE"]
    await c.invoke(
        SendMedia(
            peer=peer,
            media=InputMediaInvoice(
                title=t("donation_title"),
                description=t("donation_subtitle"),
                invoice=Invoice(
                    currency="BRL",
                    prices=[LabeledPrice(label=t("donation_label"), amount=val)],
                    test=q.from_user.id in sudos,
                ),
                payload=b"payment",
                provider=key,
                provider_data=DataJSON(data=r"{}"),
                start_param=f"pay_{val}",
            ),
            message="",
            random_id=c.rnd_id(),
        )
    )
    return


@Client.on_raw_update(group=10)
async def raw_update(c: Client, update: Update, users: dict, chats: dict):
    if isinstance(update, UpdateBotPrecheckoutQuery):
        # This is to tell Telegram that everything is okay with this order.
        await c.invoke(SetBotPrecheckoutResults(query_id=update.query_id, success=True))

    if (
        isinstance(update, UpdateNewMessage)
        and hasattr(update.message, "action")
        and isinstance(update.message.action, MessageActionPaymentSentMe)
    ):
        # Sending a message confirming the order (additional to TGs service message)
        user = users[update.message.peer_id.user_id]
        ut = use_user_lang(user.id)
        await c.send_message(user.id, ut("order_confirmed"))
        print(user.id, user.first_name, "order confirmed")
