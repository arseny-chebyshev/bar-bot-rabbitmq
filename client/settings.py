import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('CLIENT_BOT_TOKEN')
admin_list = os.getenv('ADMIN_LIST').split(', ')
