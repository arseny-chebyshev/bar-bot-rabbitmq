import pika
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram_dialog import DialogRegistry
from client.settings import bot_token, amqp_host

client_bot = Bot(token=bot_token, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(client_bot, storage=storage)
registry = DialogRegistry(dp)
amqp_conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_host))
channel = amqp_conn.channel()
