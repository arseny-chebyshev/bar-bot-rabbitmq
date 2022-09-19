from decimal import Decimal
from admin.states.admin import DishDialog
from db.models import Dish, Order
from pathlib import Path
from aiogram.dispatcher import FSMContext
from aiogram_dialog import DialogManager
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from settings import admin_list
from states.admin import AdminDialog, DishState
from keyboards.menu.kbds import *
from loader import dp
from utils import notify_admin


@dp.message_handler(commands='start')
async def start_admin(msg: Message, dialog_manager: DialogManager):
    if str(msg.from_user.id) in admin_list:
        await dialog_manager.start(AdminDialog.start)
    else:
        await msg.answer("Нет прав администратора для доступа.")

@dp.callback_query_handler(lambda c: c.data.startswith('callback'))
async def answer_callback(query: CallbackQuery):
    call = query.data[9:]
    if call.startswith('ready'):
        order = Order.objects.filter(id=int(call[5:])).first()
        order.is_ready = True
        order.save()
        await query.answer("Заказ был отмечен готовым.")
        await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(row_width=2).row(
            InlineKeyboardButton(text="Скрыть", callback_data=f"callback_hide{order.id}")
        ))
    elif call.startswith('hide'):
        await query.answer("Заказ был скрыт.")
        await query.message.delete()

@dp.message_handler(state=DishState.insert_name)
async def add_price_to_dish(msg: Message, state: FSMContext, dialog_manager: DialogManager):
    if msg.text == "❌Отмена":
        await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        await state.reset_state(with_data=True)
        await dialog_manager.start(AdminDialog.start)
    else:
        await state.update_data({'dish_name': msg.text})
        await msg.answer(f"Позиция {msg.text}. Цена:", reply_markup=cancel_menu_button)
        await DishState.insert_price.set()

@dp.message_handler(state=DishState.insert_price)
async def assert_dish(msg: Message, state: FSMContext, dialog_manager: DialogManager):
    try:
        if msg.text == "❌Отмена":
            await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
            await state.reset_state(with_data=True)
            await dialog_manager.start(AdminDialog.start)
        else:
            price = Decimal(msg.text)
            data = await state.get_data()
            dish_name = data['dish_name']
            await msg.answer(f"Подтверди создание позиции:\nНазвание: {dish_name}\nЦена: {price} LKR", 
                               reply_markup=confirm_dish_menu)
            await state.update_data({"dish_price": price})
            await DishState.confirm_dish.set()
    except BaseException:
        await msg.answer('Нужно ввести число. Остаток разделяется симоволом ".". Например: 49.99')

@dp.message_handler(state=DishState.confirm_dish)
async def create_dish(msg: Message, state: FSMContext, dialog_manager: DialogManager):
    match msg.text:
        case "✅Подтвердить":
            data = await state.get_data()
            dish_name = data["dish_name"]
            dish_price = data["dish_price"]
            if 'old_dish' in data.keys(): #приходит из dialog-запроса на изменение позиции (DishState.edit_dish)
                dish = Dish.objects.filter(id=data['old_dish']).first()
                dish.name = dish_name
                dish.price = dish_price
                dish.save()
            dish = Dish.objects.filter(name=dish_name).first()
            if dish:
                dish.price = dish_price
            else:
                dish = Dish(name=dish_name, price=dish_price)
            dish.save()
            await msg.answer(f"Позиция {dish_name} c ценой {dish_price} была создана.",
                             reply_markup=ReplyKeyboardRemove())
            await state.reset_state(with_data=True) 
            if 'old_dish' in data.keys():
                await dialog_manager.start(AdminDialog.start)
            else:
                await msg.answer("Введи имя новой позиции:", reply_markup=cancel_menu_button)
                await DishState.insert_name.set()
        case "❌Отмена":
            await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove()) 
            await state.reset_state(with_data=True)
            await dialog_manager.start(AdminDialog.start)