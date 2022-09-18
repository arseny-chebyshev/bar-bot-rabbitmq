import asyncio
import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from db.models import DishQuantity, Order
from admin.loader import admin_bot
from admin.settings import admin_id

async def notify_admin():
    while True:
        await asyncio.sleep(0.5)
        with open('../orders.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if data['orders']:
                for order in data['orders']:
                    order = Order.objects.filter(id=int(order)).first()
                    quantities = []
                    for dish in DishQuantity.objects.filter(order=order):
                        quantities.append(f"{dish.dish.name} x {dish.quantity}: {dish.dish.price * dish.quantity}LKR\n")
                    text = f"""\nНовый заказ #{order.id}
Заказал: {f'<a href="https://t.me/{order.guest.username}">{order.guest.name}</a>' if order.guest.username else order.guest.name}
Телефон гостя: {order.guest.phone}
Состав: \n{''.join(quantities)}
Сумма: {order.total}LKR"""
                    inline_kbd = InlineKeyboardMarkup(row_width=2).row(
                        InlineKeyboardButton(text="Отметить готовым", callback_data=f"callback_ready{order.id}"),
                        InlineKeyboardButton(text="Удалить", callback_data=f"callback_delete{order.id}")
                        )
                    await admin_bot.send_message(chat_id=admin_id, text=text, reply_markup=inline_kbd)
                data['orders'] = []
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
