import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('ADMIN_BOT_TOKEN')
amqp_host = os.getenv('AMQP_HOST')
