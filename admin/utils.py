import asyncio
import json
from datetime import datetime, timedelta
from db.models import DishQuantity, Order
from admin.loader import admin_bot
from admin.settings import admin_id

async def notify_admin():
    while True:
        await asyncio.sleep(3.0)
        with open('../orders.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            if data['orders']:
                for order in data['orders']:
                    order = Order.objects.filter(id=int(order)).first()
                    quantities = []
                    for dish in DishQuantity.objects.filter(order=order):
                        quantities.append(f"{dish.dish.name} x {dish.dish.price} ---- {dish.dish.price * dish.quantity}Р\n")
                    text = f"""\nНовый заказ #{order.id}\nЗаказал: {order.guest}
Состав: \n{''.join(quantities)}
Сумма: {order.total}"""
                    await admin_bot.send_message(chat_id=admin_id, text=text)
                data['orders'] = []
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
