import asyncio
import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.exceptions import ChatNotFound
from db.models import DishQuantity, Order
from admin.loader import admin_bot
from admin.settings import admin_list

async def notify_admin():
    while True:
        await asyncio.sleep(0.5)
        with open('../queue/orders.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if data['orders']:
                for order in data['orders']:
                    print(order)
                    order = Order.objects.filter(id=int(order)).first()
                    quantities = []
                    print(order)
                    for dish in DishQuantity.objects.filter(order=order):
                        quantities.append(f"{dish.dish.name} x {dish.quantity}: {dish.dish.price * dish.quantity} LKR\n")
                    text = f"""\n<strong>Новый заказ #{order.id}</strong>
Заказал: {f'<a href="https://t.me/{order.guest.username}">{order.guest.name}</a>' if order.guest.username else order.guest.name}
Телефон гостя: {order.guest.phone}
Состав: \n{''.join(quantities)}
Сумма: {order.total} LKR"""
                    inline_kbd = InlineKeyboardMarkup(row_width=2).row(
                        InlineKeyboardButton(text="Отметить готовым", callback_data=f"callback_ready{order.id}"),
                        InlineKeyboardButton(text="Скрыть", callback_data=f"callback_hide{order.id}")
                        )
                    for admin_id in admin_list:
                        try:
                            message = await admin_bot.send_message(chat_id=admin_id, text=text, reply_markup=inline_kbd)
                            asyncio.ensure_future(poll_order_message(chat_id=admin_id, message_id=message.message_id, order_id=order.id))
                        except ChatNotFound:
                            continue
            data['orders'] = []
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

async def poll_order_message(chat_id, message_id, order_id):
    while True:
        await asyncio.sleep(2)
        order = Order.objects.filter(id=order_id).first()
        if not order:
            await admin_bot.delete_message(chat_id=chat_id, message_id=message_id)
            break
        if order.is_ready:
            inline_kbd = InlineKeyboardMarkup(row_width=1).row(
                         InlineKeyboardButton(text="Скрыть", callback_data=f"callback_hide{order.id}")
                        )
            await admin_bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=inline_kbd)
            break
