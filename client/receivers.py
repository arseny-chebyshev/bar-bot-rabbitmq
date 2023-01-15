import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from client.loader import client_bot
from db.models import Order

def notify_client(ch, method, properties, body):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_notify_client(body))

async def _notify_client(body):
    order = Order.objects.filter(id=int(body)).first()
    inline_kbd = InlineKeyboardMarkup(row_width=2).row(
                         InlineKeyboardButton(text="Повторить", callback_data=f"callback_repeat{order.id}"),
                         InlineKeyboardButton(text="Сделать новый заказ", callback_data=f"callback_new")
                        )
    await client_bot.send_message(chat_id=order.guest.id, text=f"""<strong>Заказ #{order.id} готов!</strong> 
Его можно оплатить при получении.""", reply_markup=inline_kbd)
