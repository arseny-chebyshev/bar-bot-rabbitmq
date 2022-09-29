import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import Order


async def wait_for_order(bot, chat_id, order_id):
    while True:
        order = Order.objects.filter(id=order_id).first()
        if order.is_ready:
            inline_kbd = InlineKeyboardMarkup(row_width=2).row(
                         InlineKeyboardButton(text="Повторить", callback_data=f"callback_repeat{order.id}"),
                         InlineKeyboardButton(text="Сделать новый заказ", callback_data=f"callback_new")
                        )
            await bot.send_message(chat_id=chat_id, text=f"""Заказ <strong>#{order_id}</strong> готов! 
Его можно оплатить при получении.""", reply_markup=inline_kbd)
            break
        else:
            await asyncio.sleep(2.0)
