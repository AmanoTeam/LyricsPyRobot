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
from lyricspybot.locales import use_chat_lang, use_user_lang


@Client.on_callback_query(filters.regex(r"donate"))
@use_chat_lang()
async def add_donate(c: Client, q: CallbackQuery, t):
    donation_amount = int(q.data.split("_")[1]) if "_" in q.data else 1000
    if donation_amount < 650:
        return

    keyboard = [
        [
            ("+ R$ 100,00", f"donate_{donation_amount + 10000}"),
            ("+ R$ 10,00", f"donate_{donation_amount + 1000}"),
            ("+ R$ 1,00", f"donate_{donation_amount + 100}"),
            ("+ R$ 0,50", f"donate_{donation_amount + 50}"),
        ],
        [(f"R$ {donation_amount / 100!s}", f"donation_{donation_amount}")],
        [
            ("- R$ 100,00", f"donate_{donation_amount - 10000}"),
            ("- R$ 10,00", f"donate_{donation_amount - 1000}"),
            ("- R$ 1,00", f"donate_{donation_amount - 100}"),
            ("- R$ 0,50", f"donate_{donation_amount - 50}"),
        ],
    ]

    await q.edit_message_text(t("se_val"), reply_markup=ikb(keyboard))


@Client.on_message(filters.regex(r"\/start pay"))
@Client.on_callback_query(filters.regex(r"donation"))
@use_chat_lang()
async def donation(c: Client, q: CallbackQuery | Message, t):
    peer = await c.resolve_peer(q.from_user.id)
    donation_amount = (
        int(q.data.split("_")[1])
        if isinstance(q, CallbackQuery)
        else int(q.text.split("_")[1])
    )
    stripe_key = (
        stripe_token["TEST"] if q.from_user.id in sudos else stripe_token["LIVE"]
    )
    await c.invoke(
        SendMedia(
            peer=peer,
            media=InputMediaInvoice(
                title=t("donation_title"),
                description=t("donation_subtitle"),
                invoice=Invoice(
                    currency="BRL",
                    prices=[
                        LabeledPrice(label=t("donation_label"), amount=donation_amount)
                    ],
                    test=q.from_user.id in sudos,
                ),
                payload=b"payment",
                provider=stripe_key,
                provider_data=DataJSON(data=r"{}"),
                start_param=f"pay_{donation_amount}",
            ),
            message="",
            random_id=c.rnd_id(),
        )
    )


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
        user_translator = use_user_lang(user.id)
        await c.send_message(user.id, user_translator("order_confirmed"))
        print(user.id, user.first_name, "order confirmed")
