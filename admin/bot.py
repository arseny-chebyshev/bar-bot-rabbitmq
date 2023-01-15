import sys
sys.path.append('..')

from concurrent.futures import ThreadPoolExecutor
import threading
import logging
from aiogram import executor
from loader import dp, admin_bot, registry, channel
from receivers import notify_admin

async def on_startup(dispatcher):
    channel.queue_declare(queue='orders_not_ready')
    channel.basic_consume(queue='orders_not_ready', auto_ack=True, 
                          on_message_callback=notify_admin)
    th = threading.Thread(target=channel.start_consuming, daemon=True)
    th.start()


async def on_shutdown(dispatcher):
    pass


def main():
    from admin import handlers
    from keyboards.dialog import dialogs
    for dialog in dialogs:
        registry.register(dialog)
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dispatcher=dp, on_startup=on_startup)
    
if __name__ == '__main__':
    main()
