import asyncio
from aiogram import executor
import logging
from loader import dp, admin_bot, registry
from settings import admin_id
from utils import notify_admin

async def on_startup(dispatcher):
    await admin_bot.send_message(admin_id, "Starting..")
    asyncio.ensure_future(notify_admin())

async def on_shutdown(dispatcher):
    pass


def main():
    from admin import handlers
    from keyboards.dialog import dialogs
    for dialog in dialogs:
        registry.register(dialog)
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dispatcher=dp, on_startup=on_startup)
    
main()
