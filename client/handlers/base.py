from lib2to3.pytree import Base
from msilib.schema import Error
from db.models import Dish, Order, Guest
from pathlib import Path
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_dialog import DialogManager
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from settings import post_channel
from states.client import RegisterUser, DishDialog, DishState
from keyboards.menu.kbds import *
from loader import dp
from settings import admin_id


@dp.message_handler(state=RegisterUser.send_contact, content_types=aiogram.types.ContentType.CONTACT)
async def process_contact(msg: Message, state: FSMContext):
    data = await state.get_data()
    await dp.bot.send_message(chat_id=admin_id,
                              text=f"""Order: {data['order']}""")
    await msg.forward(chat_id=admin_id)
    await msg.answer("Спасибо! Заказ был оформлен. Ожидайте, я проинформирую Вас о готовности",
                     reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=True)


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


@dp.message_handler(Command('dish'))
async def select_dish_action(msg: Message, state: FSMContext):
    await msg.answer("Выбери необходимое действие:", reply_markup=dish_menu)
    await DishState.select_dish_action.set()

@dp.message_handler(state=DishState.select_dish_action)
async def continue_dish_action(msg: Message, state: FSMContext, dialog_manager: DialogManager):
    if msg.text == 'Добавить новую позицию':
        await msg.answer("Введите имя для новой позиции:", reply_markup=ReplyKeyboardRemove())
        await DishState.insert_name.set()
    elif msg.text == 'Изменить текущие позиции':
        await dialog_manager.start(DishDialog.select_dish)

@dp.message_handler(state=DishState.insert_name)
async def add_price_to_dish(msg: Message, state: FSMContext):
    await state.update_data({'dish_name': msg.text})
    await msg.answer(f"Позиция {msg.text}. Цена:")
    await DishState.insert_price.set()

@dp.message_handler(state=DishState.insert_price)
async def assert_dish(msg: Message, state: FSMContext):
    try:
        price = float(msg.text)
        data = await state.get_data()
        dish_name = data['dish_name']
        await msg.answer(f"Подтвердите ввод позиции: {dish_name}, цена: {price}", 
                           reply_markup=confirm_dish_menu)
        await state.update_data({"dish_price": price})
        await DishState.confirm_dish.set()
    except BaseException:
        await msg.answer('Нужно ввести число. Остаток разделяется симоволом ".". Например: 49.99')

@dp.message_handler(state=DishState.confirm_dish)
async def create_dish(msg: Message, state: FSMContext):
    match msg.text:
        case "Подтвердить":
            data = await state.get_data()
            dish_name = data["dish_name"]
            dish_price = data["dish_price"]
            if 'old_dish' in data.keys(): #приходит из dialog-запроса на изменение позиции (DishState.edit_dish)
                dish = Dish.objects.filter(id=data['old_dish'])
                dish.delete()
            dish = Dish.objects.filter(name=dish_name).first()
            if dish:
                dish.price = dish_price
            else:
                dish = Dish(name=dish_name, price=dish_price)
            dish.save()
            await msg.answer(f"Позиция {dish_name} c ценой {dish_price} была создана.",
                             reply_markup=ReplyKeyboardRemove()) 
            await state.reset_state(with_data=True)
        case "Отмена":
            await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
            await state.reset_state(with_data=True)    

@dp.message_handler(commands=['help'], state=None)
async def show_help(msg: Message):
    h = Path(__file__).with_name('help.txt')
    with h.open('r', encoding='utf-8') as response:
        await msg.answer(response.read(), reply_markup=ReplyKeyboardRemove())
        response.close()
