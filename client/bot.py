from aiogram import executor
from aiogram.utils.executor import start_webhook
import logging
from loader import dp, bot, registry
from settings import admin_id

async def on_startup(dispatcher):
    await bot.send_message(admin_id, "Starting..")

async def on_shutdown(dispatcher):
    pass


def main():
    import handlers
    from keyboards.dialog import dialogs
    for dialog in dialogs:
        registry.register(dialog)
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dispatcher=dp, on_startup=on_startup)

main()
