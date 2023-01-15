import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from admin.loader import admin_bot
from db.models import Order, DishQuantity, Guest

def notify_admin(ch, method, properties, body):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_notify_admin(body))

async def _notify_admin(body):
    order = Order.objects.get(id=int(body))
    quantities = [f"{dish.dish.name} x {dish.quantity}: {dish.dish.price * dish.quantity} LKR\n"
                      for dish in DishQuantity.objects.filter(order=order)]
    profile = f'<a href="https://t.me/{order.guest.username}">{order.guest.name}</a>' if order.guest.username else order.guest.name
    text = f"""\n<strong>Новый заказ #{order.id}</strong>
Заказал: {profile}
Телефон гостя: {order.guest.phone}
Состав: \n{''.join(quantities)}
Сумма: {order.total} LKR"""
    text = f"""<strong>Новый заказ #{order.id}</strong>
Заказал: {profile}
Телефон гостя: {order.guest.phone}
Состав: \n{''.join(quantities)}
Сумма: {order.total} LKR"""
    for admin in Guest.objects.filter(is_admin=True):
        try:
            message = await admin_bot.send_message(chat_id=admin.id, 
                                                   text=text, 
                                                   reply_markup=InlineKeyboardMarkup(row_width=2).row(
                        InlineKeyboardButton(text="Отметить готовым", callback_data=f"callback_ready{order.id}"),
                        InlineKeyboardButton(text="Скрыть", callback_data=f"callback_hide{order.id}")
                        ))
            print(f"message sent to admin: {message = }, {message.message_id = }")
            await poll_order_message(chat_id=admin.id, msg_id=message.message_id, order_id=order.id)
        except (ChatNotFound, BotBlocked):
            continue

async def poll_order_message(chat_id: str, msg_id: int, order_id):
    while True:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            await admin_bot.delete_message(chat_id=chat_id, message_id=msg_id)
            break
        if order.is_ready:
            inline_kbd = InlineKeyboardMarkup(row_width=1).row(
                         InlineKeyboardButton(text="Скрыть", callback_data=f"callback_hide{order.id}")
                        )
            await admin_bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=inline_kbd)
            break
        await asyncio.sleep(2)
