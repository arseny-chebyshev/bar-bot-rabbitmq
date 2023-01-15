import asyncio
import json
from decimal import Decimal
from db.models import Dish, DishQuantity, Order, Guest
from pathlib import Path
import aiogram
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_dialog import DialogManager
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.filters import Text
from states.client import RegisterUser, DishDialog, DishState
from keyboards.menu.kbds import *
from loader import dp, client_bot


@dp.message_handler(state=RegisterUser.send_contact, content_types=aiogram.types.ContentType.CONTACT)
async def process_contact(msg: Message, state: FSMContext):
    data = await state.get_data()
    guest_cred = {'id': int(msg.contact['user_id']), 
                  'name': f"{msg.contact['first_name']}{''.join([' ',msg.contact['last_name']]) if 'last_name' in dict(msg.contact).keys() else ''}",
                  'phone': msg.contact['phone_number']}
    if 'username' in dict(msg.from_user).keys():
        guest_cred['username'] = msg.from_user['username']
    guest = Guest.objects.filter(id=int(msg.contact['user_id'])).first()
    if not guest:
        guest = Guest(**guest_cred)
        guest.save()
    order = Order.objects.create(guest=guest, is_ready=False, total=Decimal(data['order']['summary']))
    for dish in data['order']['dishes']:
        order_dish = Dish.objects.filter(id=dish['id']).first()
        DishQuantity.objects.create(order=order, dish=order_dish, quantity=dish['quantity'])
    guest.debt -= data['order']['summary']
    guest.save()
    await msg.answer(f"""Спасибо! Заказ был оформлен.\n<strong>Номер заказа: {order.id}</strong>
Как только заказ будет готов, я пришлю тебе сообщение.""", reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)
    # with open('../queue/orders.json', 'r+', encoding='utf-8') as f:
    #     data = json.load(f)
    #     data['orders'].append(order.id)
    #     f.seek(0)
    #     json.dump(data, f, indent=4)
    #     f.truncate()
    # asyncio.ensure_future(wait_for_order(client_bot, msg.from_user.id, order.id))
    

@dp.message_handler(Text(equals=["❌ Отмена"]), state=RegisterUser.send_contact)
async def cancel_record(msg: Message, state: FSMContext):
    await msg.answer("Заказ отменен.", reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)

@dp.message_handler(Text(equals=["🖊 Заказать"]), state=RegisterUser.send_contact)
async def create_order(msg: Message, state: FSMContext):
    data = await state.get_data()
    guest = data['order']['guest']
    order = Order.objects.create(guest=guest, is_ready=False, total=Decimal(data['order']['summary']))
    for dish in data['order']['dishes']:
        order_dish = Dish.objects.filter(id=dish['id']).first()
        DishQuantity.objects.create(order=order, dish=order_dish, quantity=dish['quantity'])
    guest.debt -= data['order']['summary']
    guest.save()
    m = await msg.answer('⌛', reply_markup=ReplyKeyboardRemove())
    await m.delete()
    inline_kbd = InlineKeyboardMarkup(row_width=2).row(
                    InlineKeyboardButton(text="Заказать ещё", callback_data=f"callback_new"))
    await msg.answer(f"""Спасибо! Заказ был оформлен.\n<strong>Номер заказа: {order.id}</strong>
Как только заказ будет готов, я пришлю тебе сообщение.""", reply_markup=inline_kbd)
    print(type(m))
    
    await state.reset_state(with_data=True)
    # with open('../queue/orders.json', 'r+', encoding='utf-8') as f:
    #     data = json.load(f)
    #     data['orders'].append(order.id)
    #     f.seek(0)
    #     json.dump(data, f, indent=4)
    #     f.truncate()
    # asyncio.ensure_future(wait_for_order(client_bot, msg.from_user.id, order.id))

@dp.message_handler(state=RegisterUser.send_contact)
async def require_push(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, нажми на одну из кнопок. Я не смогу продолжать диалог дальше, пока они тут 😓")

@dp.message_handler(commands=["start"], state=None)
async def start(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DishDialog.select_dish)

@dp.callback_query_handler(lambda c: c.data.startswith('callback'))
async def answer_callback(query: CallbackQuery, dialog_manager=DialogManager):
    call = query.data[9:]
    if call.startswith('repeat'):
        await query.answer("Повторим!")
        old_order = Order.objects.filter(id=int(call[6:])).first()
        new_order = Order.objects.create(guest=old_order.guest, is_ready=False, total=old_order.total)
        for dish in DishQuantity.objects.filter(order=old_order):
            DishQuantity.objects.create(order=new_order, dish=dish.dish, quantity=dish.quantity)
        old_order.guest.debt -= old_order.total
        old_order.guest.save()
        await query.message.answer(f"""Спасибо! Заказ был оформлен.\n<strong>Номер заказа: {new_order.id}</strong>
Как только заказ будет готов, я пришлю тебе сообщение.""", reply_markup=ReplyKeyboardRemove())
        # with open('../queue/orders.json', 'r+', encoding='utf-8') as f:
        #     data = json.load(f)
        #     data['orders'].append(new_order.id)
        #     f.seek(0)
        #     json.dump(data, f, indent=4)
        #     f.truncate()
        # asyncio.ensure_future(wait_for_order(client_bot, query.from_user.id, new_order.id))
    elif call.startswith('new'):
        await query.answer("Новый заказ!")
        await dialog_manager.start(DishDialog.select_dish)
