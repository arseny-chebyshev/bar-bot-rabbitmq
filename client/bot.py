import sys
sys.path.append('..')

import threading
import logging
from aiogram import executor
from loader import dp, client_bot, registry, channel
from receivers import notify_client

async def on_startup(dispatcher):
    channel.queue_declare(queue='orders_ready')
    channel.basic_consume(queue='orders_ready', auto_ack=True, on_message_callback=notify_client)
    th = threading.Thread(target=channel.start_consuming, daemon=True)
    th.start()

async def on_shutdown(dispatcher):
    pass


def main():
    import handlers
    from keyboards.dialog import dialogs
    for dialog in dialogs:
        registry.register(dialog)
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dispatcher=dp, on_startup=on_startup)

if __name__ == '__main__':
    main()
