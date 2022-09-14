import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('CLIENT_BOT_TOKEN')
admin_id = os.getenv('ADMIN_ID')
post_channel = os.getenv('POST_CHANNEL_ID')

