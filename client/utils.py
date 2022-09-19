import asyncio
from db.models import Order

async def wait_for_order(bot, chat_id, order_id):
    while True:
        order = Order.objects.filter(id=order_id).first()
        if order.is_ready:
            await bot.send_message(chat_id=chat_id, text=f"""Заказ #{order_id} готов! 
Его можно оплатить при получении.""")
            break
        else:
            await asyncio.sleep(2.0)
