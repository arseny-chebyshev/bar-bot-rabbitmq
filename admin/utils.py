from admin.loader import admin_bot
from admin.settings import admin_id

async def notify_admin(text):
    print("\n\n\nNOTIFY RUNNING")
    await admin_bot.send_message(chat_id=admin_id, text=text)
