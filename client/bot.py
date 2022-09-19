from aiogram import executor
import logging
from loader import dp, client_bot, registry
from settings import admin_list

async def on_startup(dispatcher):
    pass
    """for admin_id in admin_list:
        await client_bot.send_message(admin_id, "Starting..")"""

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
