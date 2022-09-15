import asyncio
from db.models import Dish, DishQuantity, Order, Guest
from pathlib import Path
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_dialog import DialogManager
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from states.client import RegisterUser, DishDialog, DishState
from keyboards.menu.kbds import *
from loader import dp, client_bot
from admin.loader import admin_bot
from settings import admin_id


@dp.message_handler(state=RegisterUser.send_contact, content_types=aiogram.types.ContentType.CONTACT)
async def process_contact(msg: Message, state: FSMContext):
    from client.utils import wait_for_order

    data = await state.get_data()

    guest_cred = {'id': int(msg.contact['user_id']), 
                  'name': f"{msg.contact['first_name']}",
                  'phone': msg.contact['phone_number']}
    guest = Guest.objects.filter(**guest_cred).first()
    if not guest:
        guest = Guest(**guest_cred)
        guest.save()
    order = Order.objects.create(guest=guest, is_ready=False, total=float(data['order']['summary']))
    for dish in data['order']['dishes']:
        order_dish = Dish.objects.filter(id=dish['id']).first()
        DishQuantity.objects.create(order=order, dish=order_dish, quantity=dish['quantity'])
    await msg.answer(f"""Спасибо! Заказ был оформлен. Номер Вашего заказа: {order.id}
Ожидайте, я проинформирую Вас о готовности""", reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)
    await admin_bot.send_message(chat_id=admin_id, text=f"""Order: {order.id} {data['order']}""")
    asyncio.ensure_future(wait_for_order(client_bot, msg.from_user.id, order.id))

    

@dp.message_handler(Text(equals=["❌ Отмена"]), state=RegisterUser.send_contact)
async def cancel_record(msg: Message, state: FSMContext):
    await msg.answer("Запись отменена.", reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)

@dp.message_handler(state=RegisterUser.send_contact)
async def require_push(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, нажми на одну из кнопок. Я не смогу продолжать диалог дальше, пока они тут 😓")

@dp.message_handler(commands=["start"], state=None)
async def start(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DishDialog.select_dish)

@dp.message_handler(commands=['help'], state=None)
async def show_help(msg: Message):
    h = Path(__file__).with_name('help.txt')
    with h.open('r', encoding='utf-8') as response:
        await msg.answer(response.read(), reply_markup=ReplyKeyboardRemove())
        response.close()
